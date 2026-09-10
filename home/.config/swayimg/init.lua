swayimg.mode = "viewer"
swayimg.antialiasing = true
swayimg.decoration = false
swayimg.overlay = false
swayimg.exif_orientation = true

swayimg.imagelist.order = "numeric"
swayimg.imagelist.reverse = false
swayimg.imagelist.recursive = false
swayimg.imagelist.adjacent = true
swayimg.imagelist.fsmon = true

swayimg.text.visible = false

swayimg.viewer.default_scale = "optimal"
swayimg.viewer.default_position = "center"
swayimg.viewer.autocenter = true
swayimg.viewer.loop = true
swayimg.viewer.preload = 1
swayimg.viewer.set_window_background(0xff1e1e2e)

swayimg.viewer.on_key("left", function()
    swayimg.viewer.open("prev")
end)

swayimg.viewer.on_key("right", function()
    swayimg.viewer.open("next")
end)
