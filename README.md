<h1 align="center">$ noteboard</h1>

<p align="center"><img src="./screenshot.jpg"></p>

[![pypi](https://img.shields.io/pypi/v/noteboard.svg)](https://pypi.python.org/pypi/noteboard) [![downloads](https://img.shields.io/pypi/dm/noteboard.svg)](https://pypi.python.org/pypi/noteboard) [![license](https://img.shields.io/github/license/AlphaXenon/noteboard.svg)](./LICENSE.txt)

**Noteboard** is a mini command-line tool which lets you manage and store your notes & tasks in a tidy and fancy way, right inside your terminal.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
  - [from source](#from-source)
  - [via PyPI](#via-pypi)
  - [Requirements](#requirements)
- [Usage](#usage)
  - [View Boards](#view-boards)
  - [Add Item](#add-item)
  - [Remove Item](#remove-item)
  - [Clear Board](#clear-board)
  - [Tick / Mark / Star Item](#tick--mark--star-item)
  - [Edit Item](#edit-item)
  - [Tag Item](#tag-item)
  - [Run Item as Command](#run-item-as-command)
  - [Undo Previous Actions](#undo-previous-actions)
  - [Import Boards from External JSON File](#import-boards-from-external-json-file)
  - [Export Boards Data as JSON File](#export-boards-data-as-json-file)
- [Interactive Mode](#interactive-mode)
- [Cautions](#cautions)
- [Credit](#credit)
- [License](#license)

## Features

* Fancy interface ✨
* Simple & Easy to use 
* **Fast as lightning** ⚡️
* **Efficient and Effective** 💪🏻
* Manage notes & tasks in multiple boards 🗒
* **Run item as command inside terminal (subprocess)** 💨
* Import boards from external JSON files & Export boards as JSON files
* **Save & Load historic states**
* **Undo multiple actions / changes**
* **Interactive mode for dynamic operations**
* **Autocomplete & Autosuggestions in interactive mode**
* **`Gzip` compressed storage** 📚

## How the storage works

The main storage is powered by `shelve`, a Python standard library, which provides a lightweight & persistent file-based database system.
Whereas the "buffer" (the one which allows you to undo previous actions), is powered by a `pickle` object.

What makes `noteboard` special is that, the storage is compressed to `gzip` when it is not being accessed.
This greatly reduces size of the file by more than 50%. 

## Installation

### from source

```shell
$ git clone https://github.com/AlphaXenon/noteboard.git
$ cd noteboard
$ [sudo] python3 setup.py install
```

### via PyPI

`pip3 install noteboard`

### Requirements

**Python 3.6 or above**

[colorama](https://github.com/tartley/colorama) --> for stylizing interface

[prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) [optional] --> for interactive mode prompts

## Usage

```text
Positional Arguments:
    add                 [+] Add an item to a board
    remove              [-] Remove an item
    clear               [x] Clear all items on a/all boards
    tick                [✓] Tick/Untick an item
    mark                [*] Mark/Unmark an item
    star                [⭑] Star/Unstar an item
    edit                [~] Edit the text of an item
    tag                 [#] Tag an item with text
    run                 [>] Run an item as command
    undo                [^] Undo the last action
    import              [I] Import and load a JSON file, overwriting current data with it
    export              [E] Export boards as a JSON file
    reset               [R] Reset settings to default

Optional Arguments:
    -h, --help          show this help message and exit
    -st, --show-time    show boards with the added time of every items
    -i, --interactive   enter interactive mode
```

---

### View Boards

`board`

* `-st/--show-time` : show boards with the last modified time of each items
* `-i/--interactive` : enter [interactive mode](#interactive-mode)

---

### Add Item

`board add <item text>`

* `-b/--board <name>` : add the item to this board

If no `board` is given, the item will be added to the default board (configured in `config.ini`)

---

### Remove Item

`board remove <item id>`

---

### Clear Board

Remove all items in the board.

`board clear`

* `-b/--board <name>` : clear this board only

If no `board` is given, all boards will be cleared.

---

### Tick / Mark / Star Item

`board {tick, mark, star} <item id>`

Run this command again on the same item to untick/unmark/unstar the item

---

### Edit Item

`board edit <item id> <new text>`

---

### Tag Item

`board tag <item id>`

* `-t/--text <tag text>` : tag the item with this text
* `-c/--color <background color>` : set the background color `colorama.Back` of this tag (default: BLUE)

If no `text` is given, existing tag of this item will be removed.

---

### Run Item as Command

`board run <item id>`

This will spawn a subprocess to execute the command.

*NOTE: Some commands may not work properly in subprocess, such as pipes.*

**TODO:** Execute command in a peseudo terminal.

---

### Undo Previous Actions

`board undo`

#### Actions that can be undone:

* add
* remove
* clear
* edit
* import

---

### Import Boards from External JSON File

`board import <path>`

*NOTE:* This will overwrite all the current data of boards.

The JSON file must be in a valid structure simillar to the following.

```json
{
    "Board Title": [
        {
            "id": 1,
            "data": "item text",
            "time": "<timestamp>",
            "date": "<human readable date format>",
            "tick": false,
            "mark": false,
            "star": false,
            "tag": "<tag text with ANSI code (auto manipulated by noteboard)>"
        },
    ]
}
```

---

### Export Boards Data as JSON File

`board export`

* `-d/--dest <destination path>` : destination path of the exported file (directory)

The exported JSON file is named `board.json`.

---

## Interactive Mode

Use `board -i/--interactive` to enter interactive mode.

**Commands:**

1. add
2. remove
3. clear
4. edit
5. undo
6. import
7. quit

Enter an empty line to view boards. Enter an empty line in prompt to abort operation.

*NOTE: You can use quotations (`'` or `"`) to specify multiple board titles / board titles that contain spaces and item ids.*

## Cautions

Some terminal emulators may not support dimmed (`Style.DIM`) & underlined (`\033[4m`) text.

The program also uses symbols such as `⭑` and `✔` which also may not be displayed properly in some terminal emulators and Windows cmd.

### Tested On:

**Shells:** bash, zsh

**Terminal Emulators:** iTerm2

## Contributing

Feel free to open issues for bug reports and feature requests ! (If you are reporting bugs, please include the log file `~/.noteboard/noteboard.log`).

I'm currently working on the compatibility with Python 2. Any help via pull requests would be great !

## Credit

This project is inspired by Klaus Sinani's [taskbook](https://github.com/klaussinani/taskbook).

## License

[MIT Licnese](./LICENSE.txt)