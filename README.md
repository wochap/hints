Note: This is still very alpha quality software and currently only works on Linux X11, with little wayland support.

<img src="https://imgur.com/iEK4Wwl.gif" alt=""/>

The current default backend is ATSPI2, which uses accesiblitly to fetch hints.You will need to enable accessibility for your system. If you use a DE, this might just be done by default. Otherwise, there is a guide here: https://wiki.archlinux.org/title/Accessibility Look at `5 Troubleshooting`.

You will need gtk3, python3, xdotool, and atspi installed as well as the python dependencies: pygobject and pyatspi


To run you will want to bind a key to `python3 main.py`. The applicaiton will only show hints with applications that support atspi accessibility.

Here is an example of a binding on i3:

```
bindsym $mod+i exec ~/path_to_vimx/vimx/main.py
```
