#!/usr/bin/env python3
"""Shared Qt/CLI backend. Settings are last successful requests, not RGB readback."""
import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time


class ControlError(Exception):
    pass


def color(value):
    value = value.removeprefix("#").upper()
    if not re.fullmatch(r"[0-9A-F]{6}", value):
        raise ValueError("Use uma cor hexadecimal, como FF0000.")
    return value


def validate(settings):
    if not isinstance(settings, dict) or settings.get("version") != 1:
        raise ControlError("Formato de configuração inválido ou incompatível.")
    if type(settings.get("brightness")) is not int or not 1 <= settings["brightness"] <= 100:
        raise ControlError("O brilho salvo deve ficar entre 1 e 100.")
    for key in ("enabled", "restore_on_login"):
        if type(settings.get(key)) is not bool:
            raise ControlError(f"Valor inválido na configuração: {key}.")
    try:
        settings["color"] = color(settings["color"])
    except (KeyError, AttributeError, ValueError) as error:
        raise ControlError("Cor inválida na configuração.") from error
    if settings.get("effect", "color") not in ("color", "pulse", "morph", "breath", "spectrum", "rainbow"):
        raise ControlError("Efeito inválido na configuração.")
    settings.setdefault("effect", "color")
    return settings


class Controller:
    def __init__(self, home=None, runner=None, config_dir=None, state_dir=None):
        self.home = Path(home or Path.home())
        config = Path(config_dir or os.environ.get("XDG_CONFIG_HOME", self.home / ".config"))
        state = Path(state_dir or os.environ.get("XDG_STATE_HOME", self.home / ".local/state"))
        self.path = config / "alienware-control/settings.json"
        self.old_path = state / "alien-light.json"
        self.lock_path = state / "alienware-control/control.lock"
        self.binary = self.home / ".local/libexec/alienfx-cli"
        self.runner = runner or subprocess.run

    @contextmanager
    def locked(self):
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a") as lock:
            deadline = time.monotonic() + 15
            while True:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise ControlError("O controlador está ocupado. Tente novamente.")
                    time.sleep(0.05)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def load(self):
        try:
            return validate(json.loads(self.path.read_text()))
        except FileNotFoundError:
            brightness = 100
            try:
                old = json.loads(self.old_path.read_text()).get("brightness", 100)
                if type(old) is int and 1 <= old <= 100:
                    brightness = old
            except (OSError, ValueError, AttributeError):
                pass
            return dict(version=1, color="FFFFFF", brightness=brightness,
                        enabled=True, restore_on_login=True, effect="color")
        except (ValueError, OSError) as error:
            raise ControlError(f"Não foi possível ler {self.path}: {error}") from error

    def save(self, settings):
        validate(settings)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        name = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", dir=self.path.parent,
                                             prefix=".settings-", delete=False) as temp:
                name = temp.name
                json.dump(settings, temp, ensure_ascii=False, indent=2)
                temp.write("\n")
                temp.flush()
                os.fsync(temp.fileno())
            os.replace(name, self.path)
            name = None
        finally:
            if name:
                Path(name).unlink(missing_ok=True)

    def run(self, *args, native=True):
        command = [str(self.binary), *map(str, args)] if native else list(args)
        try:
            result = self.runner(command, text=True, capture_output=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ControlError(f"Falha ao executar {Path(command[0]).name}: {error}") from error
        if result.returncode:
            detail = result.stderr.strip() or result.stdout.strip() or "erro no controlador"
            raise ControlError(detail[-1500:])
        return result.stdout.strip()

    def keyboard(self):
        devices = self.run("status")
        match = re.search(r"Device #(\d+) - [^\n]*VID#0xd62, PID#0x1bbc, APIv5[^\n]*", devices)
        if not match or "(inactive)" in match.group():
            raise ControlError("Teclado indisponível. Confira a conexão e as permissões do controlador RGB.")
        return int(match.group(1))

    def hardware_apply(self, settings):
        index = self.keyboard()
        if settings["enabled"]:
            if settings.get("effect", "color") == "color":
                rgb = [int(settings["color"][i:i + 2], 16) for i in (0, 2, 4)]
                self.run("keyboardcolor", *rgb)
            else:
                effects = {"pulse": 1, "morph": 2, "breath": 3, "spectrum": 4, "rainbow": 5}
                self.run("setglobal", index, effects[settings["effect"]], 0)
        level = round(settings["brightness"] * 255 / 100) if settings["enabled"] else 0
        self.run("setdim", index, level)

    def status(self, settings=None, connected=None):
        result = dict(settings=settings or self.load(), connected=connected, error=None,
                      settings_file=str(self.path), profile=None)
        if connected is None:
            try:
                self.keyboard()
                result["connected"] = True
            except ControlError as error:
                result["connected"] = False
                result["error"] = str(error)
        try:
            result["profile"] = self.run("powerprofilesctl", "get", native=False)
        except ControlError:
            pass
        return result

    def apply(self, changes):
        settings = self.load()
        previous_brightness = settings["brightness"]
        settings.update(changes)
        if settings["brightness"] == 0:
            settings["brightness"] = previous_brightness
            settings["enabled"] = False
        validate(settings)
        self.hardware_apply(settings)
        self.save(settings)
        return self.status(settings, connected=True)

    def restore(self, if_enabled=False):
        settings = self.load()
        if not self.path.exists() or (if_enabled and not settings["restore_on_login"]):
            return dict(skipped=True, settings=settings)
        self.hardware_apply(settings)
        return self.status(settings, connected=True)

    def profile(self, profile):
        if profile not in ("power-saver", "balanced", "performance"):
            raise ControlError("Perfil de energia inválido.")
        self.run("powerprofilesctl", "set", profile, native=False)
        return self.status()

    def quiet_toggle(self):
        if self.run("powerprofilesctl", "get", native=False) == "power-saver":
            return self.profile("balanced")
        settings = self.load()
        settings["color"] = "FFFFFF"
        self.hardware_apply(settings)
        self.run("powerprofilesctl", "set", "power-saver", native=False)
        self.save(settings)
        return self.status(settings, connected=True)

    def effect(self, name):
        effects = {"pulse": 1, "morph": 2, "breath": 3, "spectrum": 4, "rainbow": 5}
        if name not in effects:
            raise ControlError("Efeito inválido. Escolha pulse, morph, breath, spectrum ou rainbow.")
        index = self.keyboard()
        # APIv5 global effects are implemented by the controller. `nc=0` is
        # accepted by this firmware and makes the built-in effect choose its colors.
        self.run("setglobal", index, effects[name], 0)
        settings = self.load()
        settings["effect"] = name
        self.save(settings)
        return self.status(settings, connected=True)


def percent(value):
    number = int(value)
    if not 0 <= number <= 100:
        raise ValueError("O brilho deve ficar entre 0 e 100.")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description="Iluminação do teclado Alienware com restauração no login.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("status", "Consultar controlador e configurações"),
                            ("white", "Aplicar branco"), ("on", "Acender"),
                            ("off", "Apagar"), ("quiet-toggle", "Alternar silencioso + branco / equilibrado")):
        commands.add_parser(name, help=help_text).add_argument("--json", action="store_true")
    c = commands.add_parser("color", help="Aplicar cor RRGGBB")
    c.add_argument("color", type=color)
    c.add_argument("--json", action="store_true")
    b = commands.add_parser("brightness", help="Ajustar brilho de 0 a 100%%")
    b.add_argument("brightness", type=percent)
    b.add_argument("--json", action="store_true")
    a = commands.add_parser("apply", help="Aplicar e salvar configurações")
    a.add_argument("--color", type=color)
    a.add_argument("--brightness", type=percent)
    a.add_argument("--enabled", choices=("on", "off"))
    a.add_argument("--persist", choices=("on", "off"))
    a.add_argument("--json", action="store_true")
    r = commands.add_parser("restore", help="Reaplicar as configurações salvas")
    r.add_argument("--if-enabled", action="store_true")
    r.add_argument("--json", action="store_true")
    p = commands.add_parser("profile", help="Selecionar perfil de energia")
    p.add_argument("profile", choices=("power-saver", "balanced", "performance"))
    p.add_argument("--json", action="store_true")
    e = commands.add_parser("effect", help="Aplicar efeito predefinido do teclado")
    e.add_argument("effect", choices=("pulse", "morph", "breath", "spectrum", "rainbow"))
    e.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    controller = Controller()
    try:
        with controller.locked():
            if args.command == "status":
                result = controller.status()
            elif args.command == "restore":
                result = controller.restore(args.if_enabled)
            elif args.command == "profile":
                result = controller.profile(args.profile)
            elif args.command == "quiet-toggle":
                result = controller.quiet_toggle()
            elif args.command == "effect":
                result = controller.effect(args.effect)
            else:
                changes = {}
                if args.command in ("white", "color"):
                    changes["color"] = "FFFFFF" if args.command == "white" else args.color
                    changes["effect"] = "color"
                elif args.command in ("on", "off"):
                    changes["enabled"] = args.command == "on"
                elif args.command == "brightness":
                    changes.update(brightness=args.brightness, enabled=args.brightness > 0)
                elif args.command == "apply":
                    for key in ("color", "brightness"):
                        if getattr(args, key) is not None:
                            changes[key] = getattr(args, key)
                    if args.enabled is not None:
                        changes["enabled"] = args.enabled == "on"
                    if args.persist is not None:
                        changes["restore_on_login"] = args.persist == "on"
                result = controller.apply(changes)
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        elif result.get("skipped"):
            print("Restauração automática desativada ou sem configuração salva.")
        else:
            s = result["settings"]
            print(f"Teclado: {'conectado' if result['connected'] else 'indisponível'} · "
                  f"#{s['color']} · brilho {s['brightness'] if s['enabled'] else 0}% · "
                  f"restaurar no login: {'sim' if s['restore_on_login'] else 'não'}")
            if result.get("error"):
                print(result["error"], file=sys.stderr)
        return 0
    except (ControlError, OSError) as error:
        if args.json:
            print(json.dumps(dict(error=str(error)), ensure_ascii=False))
        else:
            print(f"alien-light: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
