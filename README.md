Note: This is still work in progress and only works on Linux X11, with little wayland support.

<p align="center">
  <img src="https://github.com/user-attachments/assets/bca7fb8e-a4ad-435b-aa40-c26dbb017239" alt="hints" />
</p>

![demo](https://github.com/user-attachments/assets/cda0e568-a16c-4bc4-af20-7b3981cc213c)

# Installing

## System Requirements

1. You will need to have some sort of [compositing](https://wiki.archlinux.org/title/Xorg#Composite) setup so that you can properly overlay hints over windows with the correct level of transparency. Otherwise, the overlay will just cover the entire screen; not allowing you to see what is under the overlay.

2. Additionally, you will also need to have GTK3 installed. Note that GTK4 does not work as GTK 4 removes the ability to globally position windows, which we need to create the overlay of hints.

3. You will need to enable accessibility for your system. If you use a Desktop Environment, this might already be enabled by default. Otherwise, there is a guide [here, take a look at "5 Troubleshooting"](https://wiki.archlinux.org/title/Accessibility).

4. vimx depends on pyatspi as the accessibility layer to "see" elements on your screen. You will need to install this as a system package before using vimx.

| Package manager   | Shell                                   |
| ----------------- | --------------------------------------- |
| Pacman            | sudo pacman -S python-atspi             |
| Apt               | sudo apt install python3-pyatspi        |
| Dnf               | sudo dnf install python3-pyatspi        |

5. Install [pipx](https://pipx.pypa.io/stable/installation/)

6. Install [xdotool](https://github.com/jordansissel/xdotool#installation)

## Installing vimx

1. Install vimx:

```
pipx install git+https://github.com/AlfredoSequeida/vimx.git --system-site-packages
```

2. At this point, vimx should be installed, you can verify this by running `vimx` in your shell. However, you will likely not see anything unless your shell has accessible elements. You will want to bind a keyboard shortcut to `vimx` so you don't have to keep typing in a command to open it. This will depend on your OS/ window manager / desktop environment.

Here is an example of a binding on i3 by editing `.conf/i3/config`:

```
bindsym $mod+i exec vimx
```

This will bind `mod + i` to launch vimx. To stop showing hints (quit vimx), press the `Esc` key on your keyboard.

# Configuration
You can customize vimx options by editing the config file in `~/.config/vimx/config.json`.

# Usage tips
- Context menus are not accessible (by atspi), but you can use arrow keys to navigate the context menu options.
- When using the accessibility backend, you will likely find using vimx in a browser to give you a lot of hints. Sometimes so many that all of the hints overlap over each other. This is because a website can have a lot of elements that are hidden/behind other elements. Furthermore, the accessibility backend does not have a nice way to distinguish what elements are actually visible in the top level. So you might try using a plugin like vimium instead when using a browser if that bothers you.

# Contributing
The easiest way to contribute is to [become a sponsor](https://github.com/sponsors/AlfredoSequeida)

## Development
If you want to help develop vimx, first setup your environment:

1. Because python-atspi is a system package, you will need to install that for your system first using your package manager. Then you can setup a virtual environment that includes python-atspi:

```
python3 -m venv venv --system-site-packages
```

2. Activate your virtual environment for development. This will differ based on OS/shell. See the table [here](https://docs.python.org/3/library/venv.html#how-venvs-work) for instructions.

3. Install vimx as an editable package (from the repositorie's root directory):

```
pip install -e .
```
At this point, vimx should be installed locally in the virtual environment, you can run `vimx` in your shell to launch it. Any edits you make to the source code will automatically update the installation. For future development work, you can simply re-enable the virtual environment (step 2).

## Development tips
- If you are making updates that impact hints, you will most likely need to test displaying hints and might find yourself executing vimx but not being quick enough to switch to a window to see hints. To get around this, you can execute `vimx` with a short pause in your shell: `sleep 0.5; vimx`. This way you can have time to switch to a window and see any errors / logs in your shell.
