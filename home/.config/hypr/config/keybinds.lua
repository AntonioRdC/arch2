local MOD = "SUPER"
local function app(command)
    return hl.dsp.exec_cmd("uwsm app -- " .. command)
end

local cycle_fullscreen = function()
    local window = hl.get_active_window()
    if not window then
        return
    end
    local state = ((tonumber(window.fullscreen) or 0) + 1) % 3
    hl.dispatch(hl.dsp.window.fullscreen_state({ internal = state, client = state, window = window }))
end

local move_window = function(direction, pixels)
    local vectors = { left = { -1, 0 }, right = { 1, 0 }, up = { 0, -1 }, down = { 0, 1 } }
    return function()
        local window = hl.get_active_window()
        if not window then
            return
        end
        if window.floating then
            local delta = vectors[direction]
            hl.dispatch(hl.dsp.window.move({ x = delta[1] * pixels, y = delta[2] * pixels, relative = true }))
        else
            hl.dispatch(hl.dsp.window.move({ direction = direction }))
        end
    end
end

hl.bind(MOD .. " + T", app("kitty.desktop"), { description = "[Apps] terminal" })
hl.bind(MOD .. " + E", app("kitty --class yazi yazi"), { description = "[Apps] files" })
hl.bind(MOD .. " + B", app("firefox.desktop"), { description = "[Apps] browser" })
hl.bind(MOD .. " + A", app("rofi-apps"), { description = "[Apps] launcher" })
hl.bind(MOD .. " + ESCAPE", app("rofi-power"), { description = "[Session] power menu" })
hl.bind(MOD .. " + SHIFT + G", app("rofi-games"), { description = "[Games] Steam launcher" })
hl.bind(MOD .. " + SHIFT + W", app("rofi-wallpaper"), { description = "[Wallpaper] selector" })
hl.bind("CTRL + SHIFT + ESCAPE", app("kitty --class system-monitor btop"), { description = "[Apps] monitor" })
hl.bind(MOD .. " + SHIFT + M", app("org.pulseaudio.pavucontrol.desktop"), { description = "[Apps] audio control" })
hl.bind(MOD .. " + CTRL + B", app("blueman-manager"), { description = "[Apps] Bluetooth" })
hl.bind(MOD .. " + K", hl.dsp.exec_cmd("hyprctl switchxkblayout all next"), { description = "[Keyboard] switch US/ABNT2" })

hl.bind(MOD .. " + Q", hl.dsp.window.close(), { description = "[Window] close" })
hl.bind("ALT + F4", hl.dsp.window.close(), { description = "[Window] close" })
hl.bind(MOD .. " + ALT + F4", hl.dsp.window.kill(), { description = "[Window] force kill" })
hl.bind(MOD .. " + DELETE", hl.dsp.exec_cmd("uwsm stop"), { description = "[Session] exit" })
hl.bind(MOD .. " + W", hl.dsp.window.float({ action = "toggle" }), { description = "[Window] floating" })
hl.bind(MOD .. " + G", hl.dsp.group.toggle(), { description = "[Window] group" })
hl.bind("ALT + P", hl.dsp.window.pseudo(), { description = "[Window] pseudotile" })
hl.bind("SHIFT + F11", cycle_fullscreen, { description = "[Window] fullscreen cycle" })
hl.bind(MOD .. " + CTRL + H", hl.dsp.group.prev(), { description = "[Group] previous" })
hl.bind(MOD .. " + CTRL + L", hl.dsp.group.next(), { description = "[Group] next" })

for _, direction in ipairs({ "left", "right", "up", "down" }) do
    hl.bind(MOD .. " + " .. direction, hl.dsp.focus({ direction = direction }), { description = "[Focus] " .. direction })
    local x = (direction == "right" and 30) or (direction == "left" and -30) or 0
    local y = (direction == "down" and 30) or (direction == "up" and -30) or 0
    hl.bind(MOD .. " + SHIFT + " .. direction, hl.dsp.window.resize({ x = x, y = y, relative = true }), {
        description = "[Resize] " .. direction, repeating = true,
    })
    hl.bind(MOD .. " + SHIFT + CTRL + " .. direction, move_window(direction, 30), {
        description = "[Move] " .. direction, repeating = true,
    })
end

hl.bind(MOD .. " + mouse:272", hl.dsp.window.drag(), { mouse = true, description = "[Mouse] move" })
hl.bind(MOD .. " + mouse:273", hl.dsp.window.resize(), { mouse = true, description = "[Mouse] resize" })
hl.bind(MOD .. " + Z", hl.dsp.window.drag(), { mouse = true, description = "[Mouse] hold to move" })
hl.bind(MOD .. " + X", hl.dsp.window.resize(), { mouse = true, description = "[Mouse] hold to resize" })
hl.bind(MOD .. " + J", hl.dsp.layout("togglesplit"), { description = "[Dwindle] toggle split" })

for i = 1, 10 do
    local key = i % 10
    hl.bind(MOD .. " + " .. key, hl.dsp.focus({ workspace = i }), { description = "[Workspace] " .. i })
    hl.bind(MOD .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }), { description = "[Workspace] move to " .. i })
    hl.bind(MOD .. " + ALT + " .. key, hl.dsp.window.move({ workspace = i, follow = false }), { description = "[Workspace] silent move to " .. i })
end

hl.bind(MOD .. " + CTRL + RIGHT", hl.dsp.focus({ workspace = "r+1" }), { description = "[Workspace] next" })
hl.bind(MOD .. " + CTRL + LEFT", hl.dsp.focus({ workspace = "r-1" }), { description = "[Workspace] previous" })
hl.bind(MOD .. " + CTRL + DOWN", hl.dsp.focus({ workspace = "empty" }), { description = "[Workspace] empty" })
hl.bind(MOD .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }), { description = "[Workspace] next" })
hl.bind(MOD .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }), { description = "[Workspace] previous" })
hl.bind(MOD .. " + S", hl.dsp.workspace.toggle_special(), { description = "[Scratchpad] toggle" })
hl.bind(MOD .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special" }), { description = "[Scratchpad] move" })
hl.bind(MOD .. " + ALT + S", hl.dsp.window.move({ workspace = "special", follow = false }), { description = "[Scratchpad] silent move" })

local fullshot = 'sh -c \'d="$HOME/Pictures/Screenshots"; mkdir -p "$d"; grim "$d/$(date +%Y-%m-%d_%H-%M-%S).png"\''
local regionshot = 'sh -c \'d="$HOME/Pictures/Screenshots"; mkdir -p "$d"; a=$(slurp) || exit; grim -g "$a" - | satty --filename - --output-filename "$d/%Y-%m-%d_%H-%M-%S.png" --copy-command wl-copy\''
local clipboard = 'sh -c \'item=$(cliphist list | rofi -dmenu -i -p "Clipboard") || exit; printf "%s" "$item" | cliphist decode | wl-copy\''
hl.bind("PRINT", hl.dsp.exec_cmd(fullshot), { locked = true, description = "[Screenshot] full" })
hl.bind(MOD .. " + P", hl.dsp.exec_cmd(regionshot), { locked = true, description = "[Screenshot] annotate region" })
hl.bind(MOD .. " + V", hl.dsp.exec_cmd(clipboard), { description = "[Clipboard] history" })
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), { locked = true, repeating = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), { locked = true })
-- KEY_MICMUTE (248 + 8). KEY_F20 shares its XKB symbol, so use physical codes.
hl.bind("code:256", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), { locked = true })
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl --class backlight set 5%+"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl --class backlight set 5%-"), { locked = true, repeating = true })
hl.bind("XF86PerformanceMode", hl.dsp.exec_cmd("toggle-power-profile"), { locked = true, description = "[Power] performance/balanced" })
-- F7 sends KEY_F20 (190 + 8). Hyprland 0.56 stores Lua codes in sMkKeys;
-- `hyprctl binds` omits that field and may show keycode=0 for a valid bind.
hl.bind("code:198", hl.dsp.exec_cmd("toggle-quiet-profile"), { locked = true, repeating = false, description = "[Power] quiet + white/balanced" })
hl.bind("CTRL + SUPER + F24", hl.dsp.exec_cmd("toggle-touchpad"), { description = "[Input] touchpad toggle" })
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })
