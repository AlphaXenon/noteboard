# Noteboard

**Noteboard** is a mini command-line tool which lets you manage and store your notes & tasks in a tidy and fancy way.

## Features

* Fancy interface
* Lightweight & Easy to use
* Manage notes & tasks in multiple boards
* Run item as command inside terminal (subprocess)
* Import boards from external JSON files & Export boards as JSON files
* Save & Load states
* Undo previous actions / changes
* Customizable colors scheme
* Store data using the `shelve` library

## Installation

### from source

```shell
$ git clone https://github.com/AlphaXenon/noteboard.git
$ cd noteboard
$ [sudo] python3 setup.py install
```

### via PyPI

`pip3 install noteboard`

### Dependency

[colorama](https://github.com/tartley/colorama) -> for stylizing interface

## Usage

```text
Positional Arguments:
    add                 [+] Add an item to a board
    remove              [-] Remove an item
    clear               [x] Clear all items on a/all boards
    tick                [✔] Tick/Untick an item
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

### View Boards

`board`

* `-st/--show-time` : show boards with the added time of each items

#### Interactive Mode

`board -i/--interactive` : enter interactive mode

This mode allows you to operate with boards more dynamically as you can modify many items at a time.

### Add Item

`board add <item text>`

* `-b/--board <name>` : add the item to this board

If no `board` is given, the item will be added to the default board (configured in `config.ini`)

### Remove Item

`board remove <item id>`

### Clear Board

Remove all items in the board.

`board clear`

* `-b/--board <name>` : clear this board only

If no `board` is given, all boards will be cleared.

### Tick / Mark / Star Item

`board {tick, mark, star} <item id>`

Run this command again on the same item to untick/unmark/unstar the item

### Edit Item

`board edit <item id> <new text>`

### Tag Item

`board tag <item id>`

* `-t/--text <tag text>` : tag the item with this text
* `-c/--color <background color>` : set the background color `colorama.Back` of this tag (default: BLUE)

If no `text` is given, existing tag of this item will be removed.

### Run Item as Command

`board run <item id>`

This will spawn a subprocess to execute the command.

*NOTE: Some commands may not work properly in subprocess, such as pipes.*

**TODO:** Execute command in a peseudo terminal.

### Undo Previous Actions

`board undo`

#### Actions that can be undone:

* add
* remove
* clear
* edit
* import

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
            "tick": false,
            "mark": false,
            "star": false,
            "tag": "<manipulated tag text with ANSI code>"
        },
    ]
}
```

### Export Boards Data as JSON File

`board export`

* `-d/--dest <destination path>` : destination path of the exported file (directory)

The exported JSON file is named `board.json`.

### Reset to Default

`board reset`

* `-c/--config` : reset the configurations to default only

If `config` flag **is not** specified, this will delete all files inside `~/.noteboard` directory.

If `config` flag **is** specified, only `~/.noteboard/config.ini` will be set to default. This will not affect the data.

## Cautions

Some terminal emulators may not support dimmed (`Style.DIM`) & underlined (`\033[4m`) text.

The program also uses symbols such as `⭑` and `✔` which also may not be displayed properly in some terminal emulators.

### Tested On:

**Shells:** bash, zsh

**Terminal Emulators:** iTerm2

## Customizing Configurations

Path to the config file: `~/.noteboard/config.ini`

You can change the foreground color of action texts by editing `~/.noteboard/config.ini` file in the `COLORS` section.

For the available foreground colors, please refer to the [colorama](https://github.com/tartley/colorama) module.

```ini
[COLORS]
; Default colors of each actions.
; Values must be valid properties of colorama.Fore
; Values must be in upper cases.
run = LIGHTCYAN_EX
add = GREEN
remove = MAGENTA
clear = RED
tick = LIGHTYELLOW_EX
mark = CYAN
star = YELLOW
edit = BLUE
tag = LIGHTBLUE_EX
import =
export =
undo = BLUE
reset = YELLOW
```

## Credit

This project is inspired by [taskbook](https://github.com/klaussinani/taskbook), a useful command-line tool for organizing notes & tasks developed by Klaus Sinani.

## License

MIT