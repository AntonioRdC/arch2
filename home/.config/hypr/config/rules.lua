hl.window_rule({
    name = "suppress-maximize-events",
    match = { class = ".*" },
    suppress_event = "maximize",
})

hl.window_rule({
    name = "fix-xwayland-drags",
    match = { class = "^$", title = "^$", xwayland = true, float = true, fullscreen = false, pin = false },
    no_focus = true,
})

hl.window_rule({
    name = "desktop-dialogs",
    match = { class = "^(org\\.pulseaudio\\.pavucontrol|nm-connection-editor|xdg-desktop-portal-gtk|blueman-manager|com.gabm.satty)$" },
    float = true,
    center = true,
    size = "70% 70%",
})

hl.window_rule({
    name = "picture-in-picture",
    match = { title = "[Pp]icture[-\\s]?[Ii]n[-\\s]?[Pp]icture.*" },
    float = true,
    pin = true,
    size = "(monitor_w*0.25) (monitor_h*0.25)",
    move = "(monitor_w*0.73) (monitor_h*0.72)",
})

hl.window_rule({
    name = "vlc-player",
    match = { class = "^(vlc|VLC)$" },
    float = true,
    center = true,
})
