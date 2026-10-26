# translate-offline

A simple, **fully offline** translator for Windows with a Hebrew interface in the style of Google Translate.
It runs as a regular desktop window, with no browser, no local server and no open ports. It translates between about 50 languages using [Argos Translate](https://github.com/argosopentech/argos-translate) models.

## Features

- Works 100% offline. Nothing is sent anywhere.
- A native desktop window that does not start a server or listen on any port, so it never conflicts with other apps on `localhost`.
- A Hebrew right-to-left interface with automatic language detection, live translation while you type, a swap button and copy-to-clipboard.
- All languages available in Argos Translate, around 50. It translates between any two of them, pivoting through English when needed.
- A single offline installer that needs no administrator rights and no internet on the target computer.

## Requirements

- **Build machine:** Windows 10/11 (64-bit) with an internet connection, and [Inno Setup 6](https://jrsoftware.org/isinfo.php) for the installer (`winget install JRSoftware.InnoSetup`).
- **Target machine:** Windows 10/11 (64-bit). No internet needed.
- About 25 GB of free space on the build machine.

## Build

```powershell
git clone https://github.com/ariel600/translate-offline.git
cd translate-offline
powershell -ExecutionPolicy Bypass -File build.ps1 -Installer
```

This creates:

- `dist\TranslateOffline\`, a portable folder you can run directly with `python\pythonw.exe app.py`.
- `dist\translate-offline-setup.exe` and its `translate-offline-setup-N.bin` parts. These make up the offline installer, split into parts of up to 2 GB.

To include only some languages, list their codes, for example `-Languages en,he,ar,fr`.

## Install on an offline computer

1. Copy `translate-offline-setup.exe` and all of its `.bin` files into the same folder, for example on a USB drive formatted as exFAT or NTFS.
2. Run `translate-offline-setup.exe` on the offline computer.
3. Open the translator from the desktop shortcut or the Start menu.

The installer bundles the Microsoft Edge WebView2 Runtime and the Visual C++ runtime, and installs WebView2 only if it is missing.

## Files

| File | Purpose |
|---|---|
| `app.py` | The desktop app: Hebrew UI and translation through Argos Translate |
| `build.ps1` | Builds the portable folder and, with `-Installer`, the setup files |
| `download-models.py` | Downloads Argos Translate language models |
| `installer.iss` | Inno Setup script for the installer |
| `assets/` | App logo and icon, and `make_icon.py`, which generates them with Pillow |

## License

The code in this repository is released under the [MIT License](LICENSE).
The installer bundles third-party software under its own licenses. See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
