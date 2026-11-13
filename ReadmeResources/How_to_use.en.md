# How to use (v3.0.0)
## Menu
[steamlink]: https://store.steampowered.com/app/952040/_/

This program is an unofficial plugin for the Steam game [`Sync Piano Meowsack`][steamlink], used to extend the functionality of the game.
1. [Save File Analysis](#Startup Page)
2. [Chart Filtering](#)
3. [Chart Score Filtering](#)
4. [One-Click Game Launch (Steam Interface)](#)
5. [Score-Difficulty Distribution Graph](#)
6. [Chart Play Details](#)
    - Distribution histogram of all clicks within -150~+250ms
    - Normal curve fitting of the distribution histogram
    - Pie chart of all clicks within -150~+250ms
    - One-click retrieval of click records from the console
    - History display
    - Rename history records
7. And More...

## Usage Requirements
1. System: Windows only
2. Client: Developed for Steam platform; not tested on Epic platform.

## Obtain this program
[release]: https://github.com/Ginsakura/MUSYNCSave/releases
[requirements]: https://github.com/Ginsakura/MUSYNCSave/blob/main/requirements.txt
1. Download from the [release page][release]

    [latest_prerelease_svg]: https://img.shields.io/github/v/release/ginsakura/MUSYNCSave?display_name=release&label=Latest%20PreRelease&include_prereleases
    [all_tags]: https://github.com/Ginsakura/MUSYNCSave/tags
    [![Latest tag][latest_prerelease_svg]][all_tags]

    [latest_release_svg]: https://img.shields.io/github/v/release/ginsakura/MUSYNCSave?display_name=release&label=Latest%20Release
    [release]: https://github.com/Ginsakura/MUSYNCSave/releases
    [![latest release][latest_release_svg]][release]

2. Compiling from Source Code:
    Compilation Environment: Python 3.11.5, [requirements.txt][requirements]

    - No command line package:
    ```cmd
    pyinstaller --distpath ./NoCLI/ -D -i ./musync_data/Musync.ico ./Launcher.py -w
    ```
    - No command line package (single exe file):
    ```cmd
    pyinstaller --distpath ./ -F -i ./musync_data/Musync.ico ./Launcher.py -w
    ```
    - With command line package:
    ```cmd
    pyinstaller --distpath ./ WithCLI/ -D -i ./musync_data/Musync.ico ./Launcher.py
    ```
    - With command line package:
    ```cmd
    pyinstaller --distpath ./ -F -i ./musync_data/Musync.ico ./Launcher.py
    ```

## Feature Introduction
### Splash Screen
#### Header
内容施工中...
