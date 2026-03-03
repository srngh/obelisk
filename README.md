# Obelisk

Disclaimer:  
This is currently a study project to get used to GTK4 / Adwaita.  

## Introduction

Obelisk is a WIP application for managing SSH Sessions.  

Similar to other solutions it will eventually allow creating and managing a large amount of saved connections.  


## Build Instructions

This projects is built in Gnome Builder.
Since the flatpak build environment has died several times on me, I've moved to a Fedora 43 Dev Container with toolbx.

Here are the steps to setup the container.

```shell
cd Projects/obelisk/
toolbox create fedora43-toolbx --distro fedora --release 43
toolbox enter fedora43-toolbx
⬢ [soeren@toolbx obelisk]$
sudo dnf install meson msgfmt git cmake glib2-devel gtk4 python3-gobject libadwaita desktop-file-utils vte291-gtk4 python3-pip gobject-introspection

pip install -r requirements.txt

meson setup builddir --prefix=/usr
meson compile -C builddir
sudo meson install -C builddir
```

Now, to use the container for building the project, go to ~Configure Project~ (Alt+,) in Builder.
I sugest you make a backup of the default .buildconfig first.

Change the runtime to the the fedora43-toolbx container.
Lastly, open the .buildconfig file and set the run-command to obelisk.

```.buildconfig
[default-2]
name=Podman
runtime=podman:415037ec9267cbca8b712a61bcb0......851b5b5346d805yc
toolchain=default
config-opts=
run-opts=
prefix=/home/.../.cache/gnome-builder/install/obelisk/podman-415037ec9267cbca8b712a61bcb0......851b5b5346d805yc
app-id=
postbuild=
prebuild=
run-command=obelisk
```

Set the active configuration to the new ~Podman~ buildconfig and run the project.
