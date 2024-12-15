Note: This is still work in progress and only works on Linux X11, with little wayland support.

<p align="center">
  <img src="https://github.com/user-attachments/assets/bca7fb8e-a4ad-435b-aa40-c26dbb017239" alt="hints" />
</p>

![demo](https://github.com/user-attachments/assets/cda0e568-a16c-4bc4-af20-7b3981cc213c)

<p align="center">
  <a href="https://www.keytilt.xyz" target="_blank">
    <img src="https://github.com/user-attachments/assets/b44f8021-7f1f-4a60-9be4-561662266e96" alt="hints" />
  </a>
</p>

# Installing

## System Requirements

1. You will need to have some sort of [compositing](https://wiki.archlinux.org/title/Xorg#Composite) setup so that you can properly overlay hints over windows with the correct level of transparency. Otherwise, the overlay will just cover the entire screen; not allowing you to see what is under the overlay.

2. Additionally, you will also need to have GTK3 installed. Note that GTK4 does not work as GTK 4 removes the ability to globally position windows, which we need to create the overlay of hints.

3. You will need to enable accessibility for your system. If you use a Desktop Environment, this might already be enabled by default. Otherwise, there is a guide [here, take a look at "5 Troubleshooting"](https://wiki.archlinux.org/title/Accessibility).

4. hints depends on pyatspi as the accessibility layer to "see" elements on your screen. You will need to install this as a system package before using hints.

| Package manager   | Shell                                   |
| ----------------- | --------------------------------------- |
| Pacman            | sudo pacman -S python-atspi             |
| Apt               | sudo apt install python3-pyatspi        |
| Dnf               | sudo dnf install python3-pyatspi        |

5. Install [pipx](https://pipx.pypa.io/stable/installation/)

## Installing hints

1. Install hints:

```
pipx install git+https://github.com/AlfredoSequeida/hints.git --system-site-packages
```

2. At this point, hints should be installed, you can verify this by running `hints` in your shell. However, you will likely not see anything unless your shell has accessible elements. You will want to bind a keyboard shortcut to `hints` so you don't have to keep typing in a command to open it. This will depend on your OS/ window manager / desktop environment.

Here is an example of a binding on i3 by editing `.conf/i3/config`:

```
bindsym $mod+i exec hints
```

This will bind `mod + i` to launch hints. To stop showing hints (quit hints), press the `Esc` key on your keyboard.

Hits also has a scroll mode to scroll, which can also be bound to a key combination. For example:

```
bindsym $mod+y exec hints --mode scroll
```

# Documentation
For a guide on configuring and using hints, please see the [Wiki](https://github.com/AlfredoSequeida/hints/wiki).

# Contributing
The easiest ways to contribute are to:
- [Become a sponsor](https://github.com/sponsors/AlfredoSequeida). Hints is a passion project that I really wanted for myself and I am working on it on my spare time. I chose to make it free and open source so that others can benefit. If you find it valuable, donating is a nice way to say thanks. You can donate any amount you want.
- Report bugs. If you notice something is not working as expected or have an idea on how to make hints better, [open up an issue](https://github.com/AlfredoSequeida/hints/issues/new). This helps everyone out.
- If you can code, feel free to commit some code! You can see if any issues need solutions or you can create a new feature. If you do want to create a new feature, it's a good idea to create an issue first so we can align on why this feature is needed and if it has a possibility of being merged.

## Development
If you want to help develop hints, first setup your environment:

1. Because python-atspi is a system package, you will need to install that for your system first using your package manager. Then you can setup a virtual environment that includes python-atspi:

```
python3 -m venv venv --system-site-packages
```

2. Activate your virtual environment for development. This will differ based on OS/shell. See the table [here](https://docs.python.org/3/library/venv.html#how-venvs-work) for instructions.

3. Install hints as an editable package (from the repositorie's root directory):

```
pip install -e .
```
At this point, hints should be installed locally in the virtual environment, you can run `hints` in your shell to launch it. Any edits you make to the source code will automatically update the installation. For future development work, you can simply re-enable the virtual environment (step 2).

## Development tips
- If you are making updates that impact hints, you will most likely need to test displaying hints and might find yourself executing hints but not being quick enough to switch to a window to see hints. To get around this, you can execute `hints` with a short pause in your shell: `sleep 0.5; hints`. This way you can have time to switch to a window and see any errors / logs in your shell.
