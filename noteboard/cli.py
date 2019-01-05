import argparse
import sys
import os
import datetime
from colorama import init, deinit, Fore, Back, Style

from . import DIR_PATH
from .__version__ import __version__
from .storage import Storage, NoteboardException
from .utils import get_time

COLORS = {
    "add": Fore.GREEN,
    "remove": Fore.LIGHTMAGENTA_EX,
    "clear": Fore.RED,
    "run": Fore.BLUE,
    "tick": Fore.GREEN,
    "mark": Fore.YELLOW,
    "star": Fore.YELLOW,
    "tag": Fore.LIGHTBLUE_EX,
    "edit": Fore.LIGHTCYAN_EX,
    "undo": Fore.LIGHTYELLOW_EX,
    "import": "",
    "export": "",
}


def p(*args, **kwargs):
    print(" ", *args, **kwargs)


def get_color(action):
    return COLORS.get(action, "")


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
    cmd = shlex.split(i["text"])
    if "|" in cmd:
        command = i["text"]
        shell = True
    elif len(cmd) == 1:
        command = i["text"]
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
    p(color + "[+] Added item", Style.BRIGHT + str(i["id"]), color + "to", Style.BRIGHT + (board or "Board"))
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
        p(color + "[✓] Ticked item", Style.BRIGHT + str(i["id"]), color)
    else:
        p(color + "[✓] Unticked item", Style.BRIGHT + str(i["id"]), color)
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
        print(Fore.RED + "[!] Text must not be empty")
        return
    with Storage() as s:
        i = s.modify_item(item, "text", text)
    print()
    p(color + "[~] Edited text of item", Style.BRIGHT + str(i["id"]), color + "from", i["text"], color + "to", text)
    print()


def tag(args):
    color = get_color("tag")
    item = args.item
    text = args.text or ""
    c = args.color
    if len(text) > 10:
        print(Fore.RED + "[!] Tag text length should not be longer than 10 characters")
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
            star = " "
            if item["star"] is True:
                star = Fore.LIGHTYELLOW_EX + "⭑"
            # convert to from timestamp to human readable time format
            time = datetime.datetime.fromtimestamp(item["time"]).strftime("%Y/%m/%d %H:%M:%S")
            # calculate days difference between two date object
            date = datetime.datetime.strptime(item["date"], "%a %d %b %Y")
            today = datetime.datetime.strptime(get_time()[0], "%a %d %b %Y")
            days = today.day - date.day
            if days <= 0:
                day_text = ""
            else:
                day_text = Fore.LIGHTBLACK_EX + "{}d".format(days)
            if st is True:
                p(star, Fore.LIGHTMAGENTA_EX + str(item["id"]), mark, text_color + item["text"], tag_text, Fore.LIGHTBLACK_EX + "({})".format(time))
            else:
                p(star, Fore.LIGHTMAGENTA_EX + str(item["id"]), mark, text_color + item["text"], tag_text, day_text)
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
            p(Fore.RED + "[!] Already at oldest change")
            print()
            return
        print()
        p(color + Style.BRIGHT + "Last Action:")
        p(get_color(state["action"]) + "=>", state["info"])
        print()
        ask = input("[?] Continue (y/n) ? ")
        if ask != "y":
            print(Fore.RED + "[!] Operation Aborted")
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


def main():
    description = (Style.BRIGHT + "    \033[4mNoteboard" + Style.RESET_ALL + " lets you manage your " + Fore.YELLOW + "notes" + Fore.RESET + " & " + Fore.CYAN + "tasks" + Fore.RESET + " in a " + Fore.LIGHTMAGENTA_EX + "tidy" + Fore.RESET + " and " + Fore.LIGHTMAGENTA_EX + "fancy" + Fore.RESET + " way.")
    epilog = \
"""
Examples:
  $ board add "improve cli" -b "Todo List"
  $ board remove 1
  $ board clear -b "Todo List"
  $ board edit 1 "improve cli help message"
  $ board tag 1 "enhancement" -c GREEN
  $ board import ~/Documents/board.json
  $ board export ~/Documents/

{0}Made with {1}\u2764{2} by AlphaXenon{3}
""".format(Style.BRIGHT, Fore.RED, Fore.RESET, Style.RESET_ALL)
    parser = argparse.ArgumentParser(
        prog="board",
        usage="board [-h]",
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser._positionals.title = "Actions"
    parser._optionals.title = "Options"
    parser.add_argument("--version", action="version", version="noteboard " + __version__)
    parser.add_argument("-st", "--show-time", help="show boards with the added time of every items", default=False, action="store_true", dest="st")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add", help=get_color("add") + "[+] Add an item to a board" + Fore.RESET)
    add_parser.add_argument("item", help="the item you want to add", type=str, metavar="<item text>")
    add_parser.add_argument("-b", "--board", help="the board you want to add the item to (default: {})".format("Board"), type=str, metavar="<name>")
    add_parser.set_defaults(func=add)

    remove_parser = subparsers.add_parser("remove", help=get_color("remove") + "[-] Remove an item" + Fore.RESET)
    remove_parser.add_argument("item", help="id of the item you want to remove", type=int, metavar="<item id>")
    remove_parser.set_defaults(func=remove)

    clear_parser = subparsers.add_parser("clear", help=get_color("clear") + "[x] Clear all items on a/all boards" + Fore.RESET)
    clear_parser.add_argument("-b", "--board", help="clear this specific board only", type=str, metavar="<name>")
    clear_parser.set_defaults(func=clear)

    tick_parser = subparsers.add_parser("tick", help=get_color("tick") + "[✓] Tick/Untick an item" + Fore.RESET)
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

    import_parser = subparsers.add_parser("import", help=get_color("import") + "[I] Import and load boards from JSON file" + Fore.RESET)
    import_parser.add_argument("path", help="path to the target import file", type=str, metavar="<path>")
    import_parser.set_defaults(func=import_)

    export_parser = subparsers.add_parser("export", help=get_color("export") + "[E] Export boards as a JSON file" + Fore.RESET)
    export_parser.add_argument("-d", "--dest", help="destination of the exported file (default: ./board.json)", type=str, default="./board.json", metavar="<destination path>")
    export_parser.set_defaults(func=export)

    args = parser.parse_args()
    init(autoreset=True)
    try:
        args.func
    except AttributeError:
        display_board(st=args.st)
    else:
        try:
            args.func(args)
        except NoteboardException as e:
            print(Style.BRIGHT + Fore.RED + "ERROR:", str(e))
        except Exception as e:
            print(Style.BRIGHT + Fore.RED + "Uncaught Exception:", str(e))
    deinit()
