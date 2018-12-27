import argparse
import sys
import os
import datetime
from colorama import init, deinit, Fore, Back, Style

from . import DEFAULTS, COLORS, DIR_PATH
from .__version__ import __version__
from .storage import Storage, NoteboardException
from .config import load_config, init_config


def get_color(action):
    color = COLORS.get(str(action), "")
    if not color:
        return color
    return eval("Fore." + str(color))


def p(*args, **kwargs):
    print(" ", *args, **kwargs)


def print_footer():
    with Storage() as s:
        shelf = dict(s.shelf)
    ticks = 0
    marks = 0
    stars = 0
    for board in shelf:
        for item in shelf[board]:
            if item["tick"] is True:
                ticks += 1
            if item["mark"] is True:
                marks += 1
            if item["star"] is True:
                stars += 1
    p(Fore.GREEN + str(ticks), Fore.LIGHTBLACK_EX + "done •", Fore.LIGHTRED_EX + str(marks), Fore.LIGHTBLACK_EX + "marked •", Fore.LIGHTYELLOW_EX + str(stars), Fore.LIGHTBLACK_EX + "starred")


def print_total():
    with Storage() as s:
        total = s.total
    p(Fore.LIGHTCYAN_EX + "Total Items:", Style.DIM + str(total))


def run(args):
    # TODO: Use a peseudo terminal to emulate command execution
    color = get_color("run")
    item = args.item
    with Storage() as s:
        i = s.get_item(item)
    # Run
    import subprocess
    import shlex
    cmd = shlex.split(i["data"])
    if "|" in cmd:
        command = i["data"]
        shell = True
    elif len(cmd) == 1:
        command = i["data"]
        shell = True
    else:
        command = cmd
        shell = False
    execuatble = os.environ.get("SHELL", None)
    process = subprocess.Popen(command, shell=shell, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.PIPE, executable=execuatble)
    # Live stdout output
    deinit()
    print(color + "[>] Running item" + Fore.RESET, Style.BRIGHT + str(i["id"]) + Style.RESET_ALL, color + "as command...\n" + Fore.RESET)
    for line in iter(process.stdout.readline, b""):
        sys.stdout.write(line.decode("utf-8"))
    process.wait()


def add(args):
    color = get_color("add")
    item = args.item
    board = args.board
    if item.strip() == "":
        print(Back.RED + "[!]", Fore.RED + "Text must not be empty")
        return
    with Storage() as s:
        i = s.add_item(board, item)
    print()
    p(color + "[+] Added item", Style.BRIGHT + str(i["id"]), color + "to", Style.BRIGHT + (board or DEFAULTS["board"]))
    print_total()
    print()


def remove(args):
    color = get_color("remove")
    item = args.item
    with Storage() as s:
        i, board = s.remove_item(item)
    print()
    p(color + "[-] Removed item", Style.BRIGHT + str(i["id"]), color + "on", Style.BRIGHT + board)
    print_total()
    print()


def clear(args):
    color = get_color("clear")
    board = args.board
    with Storage() as s:
        amt = s.clear_board(board)
    print()
    if board:
        p(color + "[x] Cleared", Style.DIM + str(amt) + Style.RESET_ALL, color + "items on", Style.BRIGHT + board)
    else:
        p(color + "[x] Cleared", Style.DIM + str(amt) + Style.RESET_ALL, color + "items on all boards")
    print_total()
    print()


def tick(args):
    color = get_color("tick")
    item = args.item
    with Storage() as s:
        state = not s.get_item(item)["tick"]
        i = s.modify_item(item, "tick", state)
    print()
    if state is True:
        p(color + "[✔] Ticked item", Style.BRIGHT + str(i["id"]), color)
    else:
        p(color + "[✔] Unticked item", Style.BRIGHT + str(i["id"]), color)
    print()


def mark(args):
    color = get_color("mark")
    item = args.item
    with Storage() as s:
        state = not s.get_item(item)["mark"]
        i = s.modify_item(item, "mark", state)
    print()
    if state is True:
        p(color + "[*] Marked item", Style.BRIGHT + str(i["id"]))
    else:
        p(color + "[*] Unmarked item", Style.BRIGHT + str(i["id"]))
    print()


def star(args):
    color = get_color("star")
    item = args.item
    with Storage() as s:
        state = not s.get_item(item)["star"]
        i = s.modify_item(item, "star", state)
    print()
    if state is True:
        p(color + "[⭑] Starred item", Style.BRIGHT + str(i["id"]))
    else:
        p(color + "[⭑] Unstarred item", Style.BRIGHT + str(i["id"]))
    print()


def edit(args):
    color = get_color("edit")
    item = args.item
    text = args.text
    if text.strip() == "":
        print(Back.RED + "[!]", Fore.RED + "Text must not be empty")
        return
    with Storage() as s:
        i = s.modify_item(item, "data", text)
    print()
    p(color + "[~] Edited text of item", Style.BRIGHT + str(i["id"]), color + "from", i["data"], color + "to", text)
    print()


def tag(args):
    color = get_color("tag")
    item = args.item
    text = args.text or ""
    c = args.color
    if len(text) > 10:
        print(Back.RED + "[!]", Fore.RED + "Tag text length should not be longer than 10 characters")
        return
    if text != "":
        tag_color = eval("Back." + c.upper())
        tag_text = tag_color + Style.DIM + "#" + Style.RESET_ALL + tag_color + text + " " + Back.RESET
    else:
        tag_text = ""
    with Storage() as s:
        i = s.modify_item(item, "tag", tag_text)
    print()
    if text != "":
        p(color + "[#] Tagged item", Style.BRIGHT + str(i["id"]), color + "with", tag_text)
    else:
        p(color + "[#] Untagged item", Style.BRIGHT + str(i["id"]))
    print()


def display_board(st=False):
    """
    :param st=False: display time if True
    """
    with Storage() as s:
        shelf = dict(s.shelf)
    if not shelf:
        print()
        p(Style.BRIGHT + "Type", Style.BRIGHT + Fore.YELLOW + "`board --help`", Style.BRIGHT + "to get started")
    for board in shelf:
        # Print Board title
        if len(shelf[board]) == 0:
            continue
        print()
        p("\033[4m" + Style.BRIGHT + board, Fore.LIGHTBLACK_EX + "[{}]".format(len(shelf[board])))
        # Print Item
        for item in shelf[board]:
            # Mark, Text color, Tag
            mark = Fore.BLUE + "●"
            text_color = ""
            tag_text = ""
            # tick
            if item["tick"] is True:
                mark = Fore.GREEN + "✔"
                text_color = Fore.LIGHTBLACK_EX
            # mark
            if item["mark"] is True:
                if item["tick"] is False:
                    mark = Fore.LIGHTRED_EX + "!"
                text_color = Style.BRIGHT + Fore.RED
            # tag
            if item["tag"]:
                tag_text = " " + item["tag"] + " "
            # Star
            star = "  "
            if item["star"] is True:
                star = Fore.LIGHTYELLOW_EX + "⭑ "
            date_format = "%Y/%m/%d %H:%M:%S"
            dt = datetime.datetime.utcfromtimestamp(item["time"]).strftime(date_format) # string
            date = datetime.datetime.strptime(dt, date_format)  # date object
            d = int(datetime.date.today().day) - int(date.day)  # difference
            # FIXME: Timestamp different locale and timezone
            if d <= 0:
                day_text = ""
            else:
                day_text = Fore.LIGHTBLACK_EX + "{}d".format(d)
            if st is True:
                p(star + Fore.LIGHTMAGENTA_EX + str(item["id"]), mark, text_color + item["data"], tag_text, Fore.LIGHTBLACK_EX + "({})".format(dt))
            else:
                p(star + Fore.LIGHTMAGENTA_EX + str(item["id"]), mark, text_color + item["data"], tag_text, day_text)
    print()
    print_footer()
    print_total()
    print()


def undo(args):
    color = get_color("undo")
    with Storage() as s:
        state = s._States.load(rm=False)
        if state is False:
            print()
            p(Back.RED + "[!]", Fore.RED + "No available state to be undone")
            print()
            return
        print()
        p(color + Style.BRIGHT + "Last Action:")
        p(get_color(state["action"]) + "=>", state["info"])
        print()
        ask = input("[?] Continue (y/n) ? ")
        if ask != "y":
            print(Back.RED + "[!]", Fore.RED + "Operation Aborted")
            return
        s.load_state()
        print(color + "[^] Undone", get_color(state["action"]) + "=>", Style.DIM + "{}".format(state["info"]))


def import_(args):
    color = get_color("import")
    path = args.path
    with Storage() as s:
        full_path = s.import_(path)
    print()
    p(color + "[I] Imported boards from", Style.BRIGHT + full_path)
    print_total()
    print()


def export(args):
    color = get_color("export")
    dest = args.dest
    with Storage() as s:
        full_path = s.export(dest)
    print()
    p(color + "[E] Exported boards to", Style.BRIGHT + full_path)
    print()


def reset(args):
    color = get_color("reset")
    clear_config = args.config
    print()
    if clear_config is True:
        p(Back.RED + "[!]", Fore.RED + "This will reset the current configurations to default")
    else:
        p(Back.RED + "[!]", Fore.RED + "This will delete all saved data of Noteboard")
    print()
    ask = input("[?] Continue (y/n) ? ")
    if ask != "y":
        print(Back.RED + "[!]", Fore.RED + "Operation Aborted")
        return
    if clear_config is True:
        init_config()
        print(Fore.GREEN + "Done:", color + "Configurations has reset")
    else:
        for file in os.listdir(DIR_PATH):
            os.remove(os.path.join(DIR_PATH, file))
        print(Fore.GREEN + "Done:", color + "Program has reset")


def interactive_prompt():

    def invalid(text=None):
        nonlocal arrow_color
        arrow_color = Fore.RED
        if text == "":
            return
        if text is None:
            print(Fore.RED + "Invalid input")
        else:
            print(Fore.RED + str(text))
    
    def check_digit(item_ids):
        nondigit = False
        for item in items:
            if not item.isdigit():
                nondigit = True
                break
        return nondigit

    arrow_color = Fore.GREEN
    display_board()
    print(Fore.LIGHTBLACK_EX + "[Type ? for help, q or ctrl-c to quit]")
    print(Fore.LIGHTBLACK_EX + "[Commands: add/remove/clear/(un)tick/(un)mark/(un)star/edit/(un)tag/undo/import]")
    print(Fore.LIGHTBLACK_EX + "[Tips: You can use , (without space) to seperate multiple boards and items]")
    while True:
        try:
            command = input(Fore.YELLOW + Style.BRIGHT + "[Noteboard]" + Style.RESET_ALL + arrow_color + "=> " + Fore.RESET)
            command = command.strip()
            if command == "":
                # display board
                pass
            elif command in ("?", "help"):
                # print help
                parser.print_help()
                continue
            elif command == "commands":
                # show all available commands
                print(Fore.LIGHTBLACK_EX + "[Commands: add/remove/clear/(un)tick/(un)mark/(un)star/edit/(un)tag/undo/import]")
                continue
            elif command == "q":
                # quit
                confirm = input(Style.BRIGHT + "Are you sure (y/n) ? " + Style.RESET_ALL)
                if confirm in ("y", "yes"):
                    return
                continue
            elif command == "add":
                # Prompt
                text = input("[+] Item text >> ").strip()
                if not text:
                    invalid()
                    continue
                boards = input("[+] Add to (default: Board) >> ").split(",")
                boards = [board.strip() for board in boards]
                # Add
                with Storage() as s:
                    for board in boards:
                        s.add_item(board, text)
            elif command == "remove":
                # Prompt
                items = input("[-] Item id >> ").split(",")
                if check_digit(items):
                    invalid()
                    continue
                # Remove
                with Storage() as s:
                    for item in items:
                        s.remove_item(int(item))
            elif command == "clear":
                # Prompt
                boards = input("[X] Clear (default: all) >> ").split(",")
                boards = [board.strip() for board in boards]
                # Clear
                with Storage() as s:
                    if boards:
                        for board in boards:
                            s.clear_board(board)
                    else:
                        s.clear_board()
            elif command in ("tick", "mark", "star", "untick", "unmark", "unstar"):
                # Prompt
                items = input("@ Item id >> ").split(",")
                if check_digit(items):
                    invalid()
                    continue
                if command.startswith("un"):
                    # Modify
                    with Storage() as s:
                        for item in items:
                            s.modify_item(int(item), command[2:], False)
                else:
                    # Modify
                    with Storage() as s:
                        for item in items:
                            s.modify_item(int(item), command, True)
            elif command == "edit":
                # Prompt
                item = input("[~] Item id >> ")
                if not item.isdigit():
                    invalid()
                    continue
                text = input("[~] New text >> ").strip()
                if not text:
                    invalid()
                    continue
                # Edit
                with Storage() as s:
                    s.modify_item(int(item), "data", text)
            elif command == "tag":
                # Prompt
                items = input("[#] Item id >> ").split(",")
                if check_digit(items):
                    invalid()
                    continue
                text = input("[#] Tag text >> ").strip()
                if not text:
                    invalid()
                    continue
                if len(text) > 10:
                    invalid("Tag text length should not be longer than 10 characters")
                    continue
                color = input("[#] Tag color (default: BLUE) >> ").strip()
                if color == "":
                    color = "BLUE"
                # Tag
                try:
                    tag_color = eval("Back." + color.upper())
                except Exception:
                    invalid("colorama.Back has no attribute '{}'".format(color.upper()))
                    continue
                tag_text = tag_color + Style.DIM + "#" + Style.RESET_ALL + tag_color + text + " " + Back.RESET
                with Storage() as s:
                    for item in items:
                        s.modify_item(int(item), "tag", tag_text)
            elif command == "untag":
                # Prompt
                items = input("[#] Item id >> ").split(",")
                if check_digit(items):
                    invalid()
                    continue
                # Untag
                with Storage() as s:
                    for item in items:
                        s.modify_item(int(item), "tag", "")
            elif command == "undo":
                with Storage() as s:
                    state = s._States.load(rm=False)
                    if state is False:
                        invalid("No available state to be undone")
                        continue
                    print(Style.BRIGHT + "Last Action:", state["info"])
                    confirm = input("[?] Continue (y/n) ? ")
                    if confirm in ("y", "yes"):
                        # Undo
                        s.load_state()
                    else:
                        continue
            elif command == "import":
                # Prompt
                path = input("[I] File path >> ").strip()
                if path == "":
                    invalid()
                    continue
                # Import
                with Storage() as s:
                    s.import_(path)
            else:
                # invalid command
                invalid("Invalid command")
                continue
        except NoteboardException as e:
            print(Style.BRIGHT + Fore.RED + "ERROR:", str(e))
            invalid("")
            continue
        except KeyboardInterrupt:
            return
        display_board()
        arrow_color = Fore.GREEN


def main():
    global parser
    usage = "board [-h] [--version] [-st] {add,remove,clear,tick,mark,star,edit,tag,run,undo,import,export,reset}"
    description = (Style.BRIGHT + "    \033[4mNoteboard" + Style.RESET_ALL + " lets you store your " + Fore.YELLOW + "notes" + Fore.RESET + " and " + Fore.CYAN + "commands" + Fore.RESET + " in a " + Fore.LIGHTMAGENTA_EX + "fancy" + Fore.RESET + " way.")
    epilog = \
"""
Examples:
  $ board add "improve cli" -b "Noteboard Todo List"
  $ board remove 1
  $ board clear -b "Noteboard Todo List"
  $ board edit 1 "improve cli help message"
  $ board tag 1 "enhancement" -c GREEN
  $ board import ~/Documents/board.json
  $ board export ~/Documents/

Made with \u2764 by AlphaXenon
"""
    parser = argparse.ArgumentParser(
        prog="board",
        usage=usage,
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--version", action="version", version="noteboard " + __version__)
    parser.add_argument("-st", "--show-time", help="show boards with the added time of every items", default=False, action="store_true", dest="st")
    parser.add_argument("-i", "--interactive", help="enter interactive mode", default=False, action="store_true")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add", help=get_color("add") + "[+] Add an item to a board" + Fore.RESET)
    add_parser.add_argument("item", help="the item you want to add", type=str, metavar="<item text>")
    add_parser.add_argument("-b", "--board", help="the board you want to add the item to (default: {})".format(DEFAULTS["board"]), type=str, metavar="<name>")
    add_parser.set_defaults(func=add)

    remove_parser = subparsers.add_parser("remove", help=get_color("remove") + "[-] Remove an item" + Fore.RESET)
    remove_parser.add_argument("item", help="id of the item you want to remove", type=int, metavar="<item id>")
    remove_parser.set_defaults(func=remove)

    clear_parser = subparsers.add_parser("clear", help=get_color("clear") + "[x] Clear all items on a/all boards" + Fore.RESET)
    clear_parser.add_argument("-b", "--board", help="clear this specific board only", type=str, metavar="<name>")
    clear_parser.set_defaults(func=clear)

    tick_parser = subparsers.add_parser("tick", help=get_color("tick") + "[✔] Tick/Untick an item" + Fore.RESET)
    tick_parser.add_argument("item", help="id of the item you want to tick/untick", type=int, metavar="<item id>")
    tick_parser.set_defaults(func=tick)

    mark_parser = subparsers.add_parser("mark", help=get_color("mark") + "[*] Mark/Unmark an item" + Fore.RESET)
    mark_parser.add_argument("item", help="id of the item you want to mark/unmark", type=int, metavar="<item id>")
    mark_parser.set_defaults(func=mark)

    star_parser = subparsers.add_parser("star", help=get_color("star") + "[⭑] Star/Unstar an item" + Fore.RESET)
    star_parser.add_argument("item", help="id of the item you want to star/unstar", type=int, metavar="<item id>")
    star_parser.set_defaults(func=star)

    edit_parser = subparsers.add_parser("edit", help=get_color("edit") + "[~] Edit the text of an item" + Fore.RESET)
    edit_parser.add_argument("item", help="id of the item you want to edit", type=int, metavar="<item id>")
    edit_parser.add_argument("text", help="new text to replace the old one", type=str, metavar="<new text>")
    edit_parser.set_defaults(func=edit)

    tag_parser = subparsers.add_parser("tag", help=get_color("tag") + "[#] Tag an item with text" + Fore.RESET)
    tag_parser.add_argument("item", help="id of the item you want to tag", type=int, metavar="<item id>")
    tag_parser.add_argument("-t", "--text", help="text of tag (do not specify this argument to untag)", type=str, metavar="<tag text>")
    tag_parser.add_argument("-c", "--color", help="set the background color of the tag (default: BLUE)", type=str, default="BLUE", metavar="<background color>")
    tag_parser.set_defaults(func=tag)

    run_parser = subparsers.add_parser("run", help=get_color("run") + "[>] Run an item as command" + Fore.RESET)
    run_parser.add_argument("item", help="id of the item you want to run", type=int, metavar="<item id>")
    run_parser.set_defaults(func=run)

    undo_parser = subparsers.add_parser("undo", help=get_color("undo") + "[^] Undo the last action" + Fore.RESET)
    undo_parser.set_defaults(func=undo)

    import_parser = subparsers.add_parser("import", help=get_color("import") + "[I] Import and load a JSON file, overwriting the current data with it" + Fore.RESET)
    import_parser.add_argument("path", help="path to the target import file", type=str, metavar="<path>")
    import_parser.set_defaults(func=import_)

    export_parser = subparsers.add_parser("export", help=get_color("export") + "[E] Export boards as a JSON file" + Fore.RESET)
    export_parser.add_argument("-d", "--dest", help="destination of the exported file (default: ./board.json)", type=str, default="./board.json", metavar="<destination path>")
    export_parser.set_defaults(func=export)

    reset_parser = subparsers.add_parser("reset", help=get_color("reset") + "[R] Reset settings to default" + Fore.RESET)
    reset_parser.add_argument("-c", "--config", help="reset configurations only", default=False, action="store_true", dest="config")
    reset_parser.set_defaults(func=reset)

    args = parser.parse_args()
    init(autoreset=True)
    if args.interactive:
        interactive_prompt()
    else:
        try:
            try:
                args.func(args)
            except AttributeError:
                raise
            except NoteboardException as e:
                print(Back.RED + "[!]", Style.BRIGHT + Fore.RED + "ERROR:", str(e))
            except Exception as e:
                print(Back.RED + "[!]", Style.BRIGHT + Fore.RED + "Uncaught Exception:", str(e))
        except AttributeError:
            display_board(st=args.st)
    deinit()
