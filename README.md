# Obelisk

## Disclaimer
> [!Note]
> This project is still heavily WIP, so don't expect any fancy features yet.

## Introduction
Obelisk is a GTK4 / Adwaita application for managing SSH connections.
Similar to other applications it will allow creating and managing SSH connections. Emphasis is on a scalable and intuitive UI. In it's current scope the primary target audience for this is myself. I find other linux applications in this category are either:

- largely unmaintaned (asbru-cm)
- lacking in features
  - grouping connections
  - variable inheritance
- coded to a large extend by AI

## Target Features
These are the features I need or want.

### Important
- [x] Use yaml config files, so they can be modified in a text editor as well
- [x] consistent dark/light mode
- [ ] Config backups and rotation on write
- [ ] Load a large amount of connections with little performance impact (>10k)
- [ ] SSH Auth via Public Key, Password Auth
- [ ] SSH Jumphost Support
- [ ] Inherit variables from folders
- [ ] Different Config Backends to import / export connections
- [ ] Convert Configs from other backends to the obelisk format (sqlite)
- [ ] Loading Several Configs at the same time without conflicts
- [ ] Password backends (Keyring, password managers)

### Nice to have
- [ ] Split View Terminals
- [ ] Color highlighting of terminal output based on pattern matching (-> chromaterm?)

## Build Instructions
This projects is built in Gnome Builder.

### Fedora
#### 1. Clone the repository

```bash
mkdir Projects && cd Projects
git clone git@github.com:srngh/obelisk.git
cd obelisk
```

#### 2. Install dependencies
```bash
sudo dnf install meson msgfmt git cmake glib2-devel gtk4 python3-gobject libadwaita desktop-file-utils vte291-gtk4 python3-pip gobject-introspection
```

#### 3. Open the project in Gnome Builder and run it
![Screenshot of running Obelisk from Gnome Builder](https://github.com/srngh/obelisk/blob/UI/assets/images/screenshot.png?raw=true)

If the project doesn't build properly, feel free to get in touch at @soern:matrix.org.

