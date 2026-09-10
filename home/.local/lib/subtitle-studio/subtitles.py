"""Lossless ASS document handling. Only translated event text is replaced."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

TAG = re.compile(r"\{[^{}]*\}|\\h")
PLACEHOLDER = re.compile(r"\[\[ASS_\d+\]\]")
JAPANESE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
KARAOKE_STYLE = re.compile(r"romaji|kanji|romanji|romanized|japanese|日本", re.I)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def plain(text: str) -> str:
    return TAG.sub("", text).replace(r"\N", " ").replace(r"\n", " ").strip()


def seconds(timestamp: str) -> float:
    h, m, s = timestamp.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


@dataclass
class Event:
    id: int
    line: int
    fields: list[str]
    columns: list[str]

    def get(self, name: str, default: str = "") -> str:
        return self.fields[self.columns.index(name)] if name in self.columns else default

    @property
    def text(self) -> str:
        return self.get("text")

    @property
    def style(self) -> str:
        return self.get("style")

    @property
    def duration(self) -> float:
        return seconds(self.get("end")) - seconds(self.get("start"))

    @property
    def song(self) -> str:
        if re.search(r"\b(OP|opening)\b", self.style, re.I):
            return "OP"
        if re.search(r"\b(ED|ending)\b", self.style, re.I):
            return "ED"
        return ""

    def preserved_reason(self, source: str) -> str:
        if KARAOKE_STYLE.search(self.style):
            return "Japanese karaoke"
        if re.search(r"\\p[1-9]\d*\b", self.text):
            return "vector drawing"
        if re.search(r"\\[kK](?:f|o)?\d", self.text):
            return "syllable-timed karaoke"
        if not plain(self.text):
            return "effect without text"
        if source != "Japanese" and JAPANESE.search(plain(self.text)):
            return "original Japanese text"
        return ""

    def protected(self) -> tuple[str, list[str]]:
        tags: list[str] = []

        def replace(match: re.Match) -> str:
            tags.append(match.group())
            return f"[[ASS_{len(tags)-1}]]"

        return TAG.sub(replace, self.text), tags

    def restore(self, translated: str) -> str:
        protected, tags = self.protected()
        if not isinstance(translated, str) or not translated.strip():
            raise ValueError(f"Segment {self.id}: empty translation.")
        if len(translated) > max(2000, len(protected) * 8):
            raise ValueError(f"Segment {self.id}: response is too long.")
        if any(ord(c) < 32 for c in translated):
            raise ValueError(f"Segment {self.id}: use \\N for line breaks, without control characters.")
        expected_markers = PLACEHOLDER.findall(protected)
        actual_markers = PLACEHOLDER.findall(translated)
        if actual_markers != expected_markers:
            # Models occasionally omit a matching italic/color tag pair when
            # both tags sit at the edges of a line. Restore that unambiguous
            # boundary formatting before rejecting the translation. Tags that
            # occur inside dialogue still require exact markers from the model.
            prefix = []
            suffix = []
            remainder = protected
            while True:
                match = PLACEHOLDER.match(remainder)
                if not match:
                    break
                prefix.append(match.group())
                remainder = remainder[match.end():]
            while True:
                match = re.search(r"(" + PLACEHOLDER.pattern + r")$", remainder)
                if not match:
                    break
                suffix.insert(0, match.group())
                remainder = remainder[:match.start()]
            if (not actual_markers and expected_markers
                    and len(prefix) + len(suffix) == len(expected_markers)):
                translated = "".join(prefix) + translated.strip() + "".join(suffix)
            else:
                raise ValueError(f"Segment {self.id}: missing or reordered formatting markers.")
        clean = PLACEHOLDER.sub("", translated)
        if "[[ASS_" in clean or "{" in clean or "}" in clean:
            raise ValueError(f"Segment {self.id}: unexpected translation formatting.")
        if re.search(r"\\(?![Nn])", clean):
            raise ValueError(f"Segment {self.id}: unexpected ASS command.")
        result = translated.strip()
        for i, tag in enumerate(tags):
            result = result.replace(f"[[ASS_{i}]]", tag)
        if TAG.findall(result) != TAG.findall(self.text):
            raise ValueError(f"Segment {self.id}: effects were not preserved.")
        return result

    def payload(self) -> dict:
        return {"id": self.id, "start": self.get("start"), "end": self.get("end"),
                "style": self.style, "speaker": self.get("name"),
                "seconds": round(self.duration, 2), "text": self.protected()[0]}


class Document:
    def __init__(self, text: str):
        self.text = text
        self.lines = text.splitlines(keepends=True)
        self.events: list[Event] = []
        columns: list[str] = []
        section = ""
        for line_index, line in enumerate(self.lines):
            stripped = line.strip()
            if stripped.startswith("["):
                section = stripped.lower()
            if section != "[events]":
                continue
            if stripped.lower().startswith("format:"):
                columns = [s.strip().lower() for s in stripped.split(":", 1)[1].split(",")]
                if not columns or columns[-1] != "text":
                    raise ValueError("Unsupported ASS: Text must be the last Events column.")
            elif line.startswith("Dialogue:"):
                if not {"start", "end", "text", "style"}.issubset(columns):
                    raise ValueError("Invalid ASS: incomplete Events header.")
                fields = line.rstrip("\r\n").split(":", 1)[1].split(",", len(columns) - 1)
                if len(fields) != len(columns):
                    raise ValueError(f"Invalid ASS at line {line_index + 1}.")
                event = Event(len(self.events), line_index, fields, columns.copy())
                if event.duration < 0:
                    raise ValueError(f"Segment {event.id}: negative duration.")
                self.events.append(event)
        if not self.events:
            raise ValueError("The track contains no subtitle events.")

    def selected(self, source: str) -> list[Event]:
        return sorted((e for e in self.events if not e.preserved_reason(source)),
                      key=lambda e: (seconds(e.get("start")), e.id))

    def render(self, translations: dict[str, str], source: str) -> tuple[str, list[dict]]:
        selected = self.selected(source)
        expected = {str(e.id) for e in selected}
        if set(translations) != expected:
            missing = sorted(expected - translations.keys(), key=int)
            extra = sorted(translations.keys() - expected)
            raise ValueError(f"Incomplete coverage. Missing: {missing[:15]}; extras: {extra[:15]}.")
        lines = self.lines.copy()
        warnings = []
        for event in selected:
            restored = event.restore(translations[str(event.id)])
            old_line = lines[event.line]
            # Preserve prefix, every metadata column, comments, styles and original line endings.
            prefix = old_line.rstrip("\r\n").rsplit(event.text, 1)[0] if event.text else old_line.rstrip("\r\n")
            newline = "\r\n" if old_line.endswith("\r\n") else "\n" if old_line.endswith("\n") else ""
            lines[event.line] = prefix + restored + newline
            visible = plain(restored)
            cps = len(visible) / max(event.duration, 0.01)
            if cps > 23:
                warnings.append({"id": event.id, "start": event.get("start"), "kind": "reading_speed",
                                 "detail": f"{cps:.1f} characters/s", "text": visible})
            if restored.count(r"\N") > 1:
                warnings.append({"id": event.id, "start": event.get("start"), "kind": "line_count",
                                 "detail": "More than two explicit lines", "text": visible})
            if visible == plain(event.text) and len(visible.split()) >= 4:
                warnings.append({"id": event.id, "start": event.get("start"), "kind": "review",
                                 "detail": "Same as source; check whether this is a name or incantation", "text": visible})
        result = "".join(lines)
        check = Document(result)
        if len(check.events) != len(self.events):
            raise ValueError("Event count changed.")
        for before, after in zip(self.events, check.events):
            if before.fields[:-1] != after.fields[:-1]:
                raise ValueError(f"Timing or style changed in segment {before.id}.")
        return result, warnings


def make_blocks(events: list[Event], size: int = 16, context: int = 3) -> list[dict]:
    """Bound both event count and source length so long signs cannot fill the context."""
    if not 1 <= size <= 24:
        raise ValueError("Block size must be between 1 and 24 segments.")
    groups: list[tuple[int, int]] = []
    start = 0
    while start < len(events):
        end, chars = start, 0
        while end < len(events) and end - start < size:
            cost = len(events[end].protected()[0])
            if end > start and chars + cost > 1800:
                break
            chars += cost
            end += 1
        groups.append((start, end))
        start = end
    return [{"number": i + 1, "before": [e.payload() for e in events[max(0, a-context):a]],
             "items": [e.payload() for e in events[a:b]],
             "after": [e.payload() for e in events[b:b+context]]}
            for i, (a, b) in enumerate(groups)]


def translation_plan(events: list[Event]) -> tuple[list[Event], dict[str, dict]]:
    """One translation for stacked text/shadow layers; retain each layer's own tags."""
    groups: dict[tuple, list[Event]] = {}
    for event in events:
        groups.setdefault((event.get("start"), event.get("end"), plain(event.text)), []).append(event)
    aliases = {}
    for group in groups.values():
        canonical = max(group, key=lambda e: len(e.protected()[1]))
        canonical_text = canonical.protected()[0]
        for event in group:
            if event.id == canonical.id:
                continue
            text = event.protected()[0]
            if text == canonical_text:
                aliases[str(event.id)] = {"canonical": str(canonical.id), "mode": "same"}
            else:
                outer = re.fullmatch(r"((?:\[\[ASS_\d+\]\])*)(.*?)((?:\[\[ASS_\d+\]\])*)", text)
                if outer and not PLACEHOLDER.search(outer[2]):
                    aliases[str(event.id)] = {"canonical": str(canonical.id), "mode": "outer",
                                               "prefix": outer[1], "suffix": outer[3]}
    return [e for e in events if str(e.id) not in aliases], aliases


def apply_aliases(translations: dict[str, str], aliases: dict[str, dict], events: dict[str, Event]):
    for idx, info in aliases.items():
        if info["canonical"] not in translations:
            continue
        value = translations[info["canonical"]]
        if info["mode"] == "outer":
            value = info["prefix"] + PLACEHOLDER.sub("", value) + info["suffix"]
        events[idx].restore(value)
        translations[idx] = value
