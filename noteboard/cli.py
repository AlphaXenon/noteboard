import argparse
import sys
import os
import re
import cmd
import shlex
import traceback
import logging
from colorama import init, deinit, Fore, Back, Style

from . import DEFAULT_BOARD, TAGS
from .__version__ import __version__
from .storage import Storage, NoteboardException
from .utils import time_diff, add_date, to_timestamp, to_datetime

# trying to import the optional prompt toolkit library
PPT = True
try:
    from prompt_toolkit import prompt
    from prompt_toolkit.shortcuts import confirm
    from prompt_toolkit.styles import Style as PromptStyle
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.validation import Validator, ValidationError
except ImportError:
    PPT = False

logger = logging.getLogger("noteboard")
COLORS = {
    "add": Fore.GREEN,
    "remove": Fore.LIGHTMAGENTA_EX,
    "clear": Fore.RED,
    "run": Fore.BLUE,
    "tick": Fore.GREEN,
    "mark": Fore.YELLOW,
    "star": Fore.YELLOW,
    "tag": Fore.LIGHTBLUE_EX,
    "due": Fore.LIGHTBLUE_EX,
    "edit": Fore.LIGHTCYAN_EX,
    "move": Fore.LIGHTCYAN_EX,
    "rename": Fore.LIGHTCYAN_EX,
    "undo": Fore.LIGHTCYAN_EX,
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
    items = args.item
    board = args.board
    with Storage() as s:
        print()
        for item in items:
            if not item:
                print(Fore.RED + "[!] Text must not be empty")
                return
            i = s.add_item(board, item)
            p(color + "[+] Added item", Style.BRIGHT + str(i["id"]), color + "to", Style.BRIGHT + (board or DEFAULT_BOARD))
    print_total()
    print()


def remove(args):
    color = get_color("remove")
    items = args.item
    with Storage() as s:
        print()
        for item in items:
            i, board = s.remove_item(item)
            p(color + "[-] Removed item", Style.BRIGHT + str(i["id"]), color + "on", Style.BRIGHT + board)
    print_total()
    print()


def clear(args):
    color = get_color("clear")
    boards = args.board
    with Storage() as s:
        print()
        if boards:
            for board in boards:
                amt = s.clear_board(board)
                p(color + "[x] Cleared", Style.DIM + str(amt) + Style.RESET_ALL, color + "items on", Style.BRIGHT + board)
        else:
            amt = s.clear_board(None)
            p(color + "[x] Cleared", Style.DIM + str(amt) + Style.RESET_ALL, color + "items on all boards")
    print_total()
    print()


def tick(args):
    color = get_color("tick")
    items = args.item
    with Storage() as s:
        print()
        for item in items:
            state = not s.get_item(item)["tick"]
            i = s.modify_item(item, "tick", state)
            if state is True:
                p(color + "[✓] Ticked item", Style.BRIGHT + str(i["id"]), color)
            else:
                p(color + "[✓] Unticked item", Style.BRIGHT + str(i["id"]), color)
    print()


def mark(args):
    color = get_color("mark")
    items = args.item
    with Storage() as s:
        print()
        for item in items:
            state = not s.get_item(item)["mark"]
            i = s.modify_item(item, "mark", state)
            if state is True:
                p(color + "[*] Marked item", Style.BRIGHT + str(i["id"]))
            else:
                p(color + "[*] Unmarked item", Style.BRIGHT + str(i["id"]))
    print()


def star(args):
    color = get_color("star")
    items = args.item
    with Storage() as s:
        print()
        for item in items:
            state = not s.get_item(item)["star"]
            i = s.modify_item(item, "star", state)
            if state is True:
                p(color + "[⭑] Starred item", Style.BRIGHT + str(i["id"]))
            else:
                p(color + "[⭑] Unstarred item", Style.BRIGHT + str(i["id"]))
    print()


def edit(args):
    color = get_color("edit")
    item = args.item
    text = (args.text or "").strip()
    if text == "":
        print(Fore.RED + "[!] Text must not be empty")
        return
    with Storage() as s:
        i = s.modify_item(item, "text", text)
    print()
    p(color + "[~] Edited text of item", Style.BRIGHT + str(i["id"]), color + "from", i["text"], color + "to", text)
    print()


def tag(args):
    color = get_color("tag")
    items = args.item
    text = (args.text or "").strip()
    c = args.color or TAGS.get(text, "") or TAGS["default"]
    if len(text) > 10:
        print(Fore.RED + "[!] Tag text length should not be longer than 10 characters")
        return
    if text != "":
        try:
            tag_color = eval("Back." + c.upper())
        except AttributeError:
            print(Fore.RED + "[!] 'colorama.AnsiBack' object has no attribute '{}'".format(c.upper()))
            return
        tag_text = tag_color + " " + Fore.BLACK + text.replace(" ", "-") + Fore.RESET + " " + Back.RESET
    else:
        tag_text = ""
    with Storage() as s:
        print()
        for item in items:
            i = s.modify_item(item, "tag", tag_text)
            if text != "":
                p(color + "[#] Tagged item", Style.BRIGHT + str(i["id"]), color + "with", tag_text)
            else:
                p(color + "[#] Untagged item", Style.BRIGHT + str(i["id"]))
    print()


def due(args):
    color = get_color("due")
    items = args.item
    date = args.date or ""
    if date and not re.match(r"\d+[d|w]", date):
        print(Fore.RED + "[!] Invalid date pattern format")
        return
    match = re.findall(r"\d+[d|w]", date)
    if date:
        days = 0
        for m in match:
            if m[-1] == "d":
                days += int(m[:-1])
            elif m[-1] == "w":
                days += int(m[:-1]) * 7
        duedate = add_date(days)
        ts = to_timestamp(duedate)
    else:
        ts = None

    with Storage() as s:
        print()
        for item in items:
            s.modify_item(item, "due", ts)
            if ts:
                p(color + "[:] Assigned due date", duedate, color + "to", Style.BRIGHT + str(item))
            else:
                p(color + "[:] Unassigned due date of item", Style.BRIGHT + str(item))
    print()


def move(args):
    color = get_color("move")
    items = args.item
    board = args.board
    with Storage() as s:
        print()
        for item in items:
            s.move_item(item, board)
            p(color + "[&] Moved item", Style.BRIGHT + str(item), color + "to", Style.BRIGHT + board)
    print()


def rename(args):
    color = get_color("rename")
    board = args.board
    new = (args.new or "").strip()
    if new == "":
        print(Fore.RED + "[!] Board name must not be empty")
        return
    with Storage() as s:
        print()
        s.get_board(board)  # try to get -> to test existence of the board
        s.shelf[new] = s.shelf.pop(board)
        p(color + "[~] Renamed", Style.BRIGHT + board, color + "to", Style.BRIGHT + new)
    print()


def undo(args):
    color = get_color("undo")
    with Storage() as s:
        state = s._States.load(rm=False)
        if state is False:
            print(Fore.RED + "[!] Already at oldest change")
            return
        print()
        p(color + Style.BRIGHT + "Last Action:")
        p("=>", get_color(state["action"]) + state["info"])
        print()
        ask = input("[?] Continue (y/n) ? ")
        if ask != "y":
            print(Fore.RED + "[!] Operation aborted")
            return
        s.load_state()
        print(color + "[^] Undone", "=>", get_color(state["action"]) + state["info"])


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
    path = os.path.abspath(os.path.expanduser(dest))
    if os.path.isfile(path):
        print(Fore.YELLOW + "[!] File {} already exists".format(path))
        ask = input("[?] Overwrite (y/n) ? ")
        if ask != "y":
            print(Fore.RED + "[!] Operation aborted")
            return
    with Storage() as s:
        full_path = s.export(path)
    print()
    p(color + "[E] Exported boards to", Style.BRIGHT + full_path)
    print()


def display_board(shelf, date=False, timeline=False, im=False):
    # print initial help message
    if not shelf:
        print()
        if im is True:
            c = "`help`"
        else:
            c = "`board --help`"
        p(Style.BRIGHT + "Type", Style.BRIGHT + Fore.YELLOW + c, Style.BRIGHT + "to get started")

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

            # Day difference
            days = time_diff(item["time"]).days
            if days <= 0:
                day_text = ""
            else:
                day_text = Fore.LIGHTBLACK_EX + "{}d".format(days)

            # Due date
            due_text = ""
            color = ""
            if item["due"]:
                due_days = time_diff(item["due"], reverse=True).days + 1  # + 1 because today is included
                if due_days == 0:
                    text = "today"
                    color = Fore.RED
                elif due_days == 1:
                    text = "tomorrow"
                    color = Fore.YELLOW
                elif due_days == -1:
                    text = "yesterday"
                    color = Fore.BLUE
                elif due_days < 0:
                    text = "{}d ago".format(due_days*-1)
                elif due_days > 0:
                    text = "{}d".format(due_days)
                due_text = "{}(due: {}{})".format(Fore.LIGHTBLACK_EX, color + text, Style.RESET_ALL + Fore.LIGHTBLACK_EX)

            # print text all together
            if date is True and timeline is False:
                p(star, Fore.LIGHTMAGENTA_EX + str(item["id"]).rjust(2), mark, text_color + item["text"], tag_text, Fore.LIGHTBLACK_EX + str(item["date"]),
                  (Fore.LIGHTBLACK_EX + "(due: {})".format(color + str(to_datetime(item["due"])) + Fore.LIGHTBLACK_EX)) if item["due"] else "")
            else:
                p(star, Fore.LIGHTMAGENTA_EX + str(item["id"]).rjust(2), mark, text_color + item["text"] + (Style.RESET_ALL + Fore.LIGHTBLUE_EX + "  @" + item["board"] if timeline else ""),
                  tag_text, day_text, due_text)
    print()
    print_footer()
    print_total()
    print()


if PPT:
    # Define Interactive Mode related objects and functions here if prompt_toolkit is installed

    def action(func):
        """A decorator function for catching exceptions of an action."""

        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except NoteboardException as e:
                print(Style.BRIGHT + Fore.RED + "ERROR:", str(e))
                logger.debug("ERROR:", exc_info=True)
            except Exception:
                exc = sys.exc_info()
                exc = traceback.format_exception(*exc)
                print(Style.BRIGHT + Fore.RED + "Uncaught Exception:\n", *exc)
                logger.debug("Uncaught Exception:", exc_info=True)
            else:
                return result

        return inner

    class InteractivePrompt(cmd.Cmd):

        class ItemValidator(Validator):

            def __init__(self, all_ids):
                self.all_ids = all_ids
                Validator.__init__(self)

            def validate(self, document):
                text = document.text.strip()
                if text:
                    try:
                        items = shlex.split(text)
                    except ValueError:
                        # ValueError("No closing quotations.")
                        items = text.split(" ")
                    for item in items:
                        if not item.isdigit():
                            raise ValidationError(message="Input contains non-numeric characters")
                        if int(item) not in self.all_ids:
                            raise ValidationError(message="Item '{}' does not exist".format(item))

        intro = "{0}[Interactive Mode]{1} Type help or ? to list all available commands.".format(Fore.LIGHTMAGENTA_EX, Fore.RESET)
        prompt = "{}@{}(noteboard){}➤{}".format(Fore.CYAN, Style.BRIGHT + Fore.YELLOW, Fore.RESET, Style.RESET_ALL) + " "
        commands = ["add", "remove", "clear", "edit", "move", "undo", "import", "quit"]

        def do_help(self, arg):
            print(Fore.LIGHTCYAN_EX + "Commands:   ", "    ".join(self.commands))

        @action
        def do_add(self, arg):
            with Storage() as s:
                all_boards = s.boards
            # completer
            board_completer = WordCompleter(all_boards)
            # prompt
            print(Fore.LIGHTBLACK_EX + "You can use quotations to specify item text that contain spaces or specify multiple items.")
            items = prompt("[?] Item text: ").strip()
            items = shlex.split(items)
            if not items:
                print(Fore.RED + "[!] Operation aborted")
                return

            board = prompt("[?] Board: ", completer=board_completer, complete_while_typing=True).strip()
            if not board:
                print(Fore.RED + "[!] Operation aborted")
            # do add item
            with Storage() as s:
                for item in items:
                    s.add_item(board, item)

        @action
        def do_remove(self, arg):
            with Storage() as s:
                all_ids = s.ids
            if not all_ids:
                print(Fore.RED + "[!] No item to be removed")
                return
            # completer
            item_completer = WordCompleter([str(id) for id in all_ids])
            print(Fore.LIGHTBLACK_EX + "You can use quotations to specify multiple items.")
            answer = prompt("[?] Item id: ", completer=item_completer, validator=self.ItemValidator(all_ids), complete_while_typing=True).strip()
            ids = shlex.split(answer)
            if not ids:
                print(Fore.RED + "[!] Operation aborted")
                return
            # do remove item
            with Storage() as s:
                for id in ids:
                    s.remove_item(int(id))

        @action
        def do_clear(self, arg):
            with Storage() as s:
                all_boards = s.boards
            if not all_boards:
                print(Fore.RED + "[!] No board to be cleared")
                return
            all_boards_quotes = ['"' + b + '"' for b in all_boards]  # to make autocompletion more convenient
            # validator for validating board existence
            class BoardValidator(Validator):
                def validate(self, document):
                    text = document.text.strip()
                    if text and text != "all":
                        try:
                            boards = shlex.split(text)
                        except ValueError:
                            # ValueError("No closing quotations.")
                            boards = text.split(" ")
                        for board in boards:
                            if board not in all_boards:
                                raise ValidationError(message="Board '{}' does not exist".format(board))
            # completer
            board_completer = WordCompleter(all_boards_quotes)
            # prompt
            print(Fore.LIGHTBLACK_EX + "You can use quotations to specify board titles that contain spaces or specify multiple boards.")
            answer = prompt("[?] Board (`all` to clear all boards): ", completer=board_completer, validator=BoardValidator(), complete_while_typing=True).strip()
            if not answer:
                print(Fore.RED + "[!] Operation aborted")
                return
            elif answer == "all":
                # clear all boards
                if not confirm("[!] Clear all boards ?"):
                    print(Fore.RED + "[!] Operation aborted")
                    return
            # do clear boards
            with Storage() as s:
                if answer == "all":
                    s.clear_board()
                else:
                    boards = shlex.split(answer)
                    for board in boards:
                        s.clear_board(board=board)

        @action
        def do_edit(self, arg):
            with Storage() as s:
                all_ids = s.ids
            if not all_ids:
                print(Fore.RED + "[!] No item to be removed")
                return
            # completer
            item_completer = WordCompleter([str(id) for id in all_ids])
            # prompt
            print(Fore.LIGHTBLACK_EX + "You can use quotations to specify multiple items.")
            items = prompt("[?] Item id: ", completer=item_completer, validator=self.ItemValidator(all_ids), complete_while_typing=True).strip()
            ids = shlex.split(items)
            if not ids:
                print(Fore.RED + "[!] Operation aborted")
                return
            text = prompt("[?] New text: ").strip()
            if not text:
                print(Fore.RED + "[!] Operation aborted")
                return
            # do edit item
            with Storage() as s:
                for id in ids:
                    s.modify_item(int(id), "text", text)

        @action
        def do_move(self, arg):
            with Storage() as s:
                all_ids = s.ids
                all_boards = s.boards
            if not all_ids:
                print(Fore.RED + "[!] No item to be moved")
                return
            # completer
            item_completer = WordCompleter([str(id) for id in all_ids])
            # prompt
            print(Fore.LIGHTBLACK_EX + "You can use quotations to specify multiple items.")
            items = prompt("[?] Item id: ", completer=item_completer, validator=self.ItemValidator(all_ids), complete_while_typing=True).strip()
            ids = shlex.split(items)
            if not ids:
                print(Fore.RED + "[!] Operation aborted")
                return
            # completer
            board_completer = WordCompleter(all_boards)
            # prompt
            board = prompt("[?] Destination board: ", completer=board_completer, complete_while_typing=True).strip()
            if not board:
                print(Fore.RED + "[!] Operation aborted")
                return
            # do move item
            with Storage() as s:
                for id in ids:
                    s.move_item(int(id), board)

        @action
        def do_undo(self, arg):
            with Storage() as s:
                state = s._States.load(rm=False)
                if state is False:
                    print(Fore.RED + "[!] Already at oldest change")
                    return
                print(get_color("undo") + Style.BRIGHT + "Last Action:")
                print("=>", get_color(state["action"]) + state["info"])
                if not confirm("[!] Continue ?"):
                    print(Fore.RED + "[!] Operation aborted")
                    return
                s.load_state()

        @action
        def do_import(self, arg):
            # validator for validating existence of file / directory of the path
            class PathValidator(Validator):
                def validate(self, document):
                    text = document.text.strip()
                    if text:
                        path = os.path.abspath(text)
                        if os.path.isdir(path):
                            raise ValidationError(message="Path '{}' is a directory".format(path))
                        if not os.path.isfile(path):
                            raise ValidationError(message="File '{}' does not exist".format(path))
            # prompt
            answer = prompt("[?] File path: ", validator=PathValidator()).strip()
            if not answer:
                print(Fore.RED + "[!] Operation aborted")
                return
            # do import
            with Storage() as s:
                s.import_(answer)

        def do_quit(self, arg):
            sys.exit(0)

        def default(self, line):
            print(Style.BRIGHT + Fore.RED + "ERROR:", "Invalid command '{}'".format(line))
            return line

        def postcmd(self, stop, line):
            if line not in self.commands:
                return
            with Storage() as s:
                shelf = dict(s.shelf)
            display_board(shelf, im=True)

        def emptyline(self):
            with Storage() as s:
                shelf = dict(s.shelf)
            display_board(shelf, im=True)


def main():
    description = (Style.BRIGHT + "    \033[4mNoteboard" + Style.RESET_ALL + " lets you manage your " + Fore.YELLOW + "notes" + Fore.RESET + " & " + Fore.CYAN + "tasks" + Fore.RESET
                   + " in a " + Fore.LIGHTMAGENTA_EX + "tidy" + Fore.RESET + " and " + Fore.LIGHTMAGENTA_EX + "fancy" + Fore.RESET + " way.")
    epilog = \
"""
Examples:
  $ board add "improve cli" -b "Todo List"
  $ board remove 2 4
  $ board clear "Todo List" "Coding"
  $ board edit 1 "improve cli"
  $ board tag 1 6 -t "enhancement" -c GREEN
  $ board tick 1 5 9
  $ board move 2 3 "Destination"
  $ board import ~/Documents/board.json
  $ board export ~/Documents/save.json

{0}Made with {1}\u2764{2} by a1phat0ny{3} (https://github.com/a1phat0ny/noteboard)
""".format(Style.BRIGHT, Fore.RED, Fore.RESET, Style.RESET_ALL)
    parser = argparse.ArgumentParser(
        prog="board",
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser._positionals.title = "Actions"
    parser._optionals.title = "Options"
    parser.add_argument("--version", action="version", version="noteboard " + __version__)
    parser.add_argument("-d", "--date", help="show boards with the added date of every item", default=False, action="store_true", dest="d")
    parser.add_argument("-s", "--sort", help="show boards with items on each board sorted alphabetically", default=False, action="store_true", dest="s")
    parser.add_argument("-t", "--timeline", help="show boards in timeline view, ignore the -d/--date option", default=False, action="store_true", dest="t")
    parser.add_argument("-i", "--interactive", help="enter interactive mode", default=False, action="store_true", dest="i")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add", help=get_color("add") + "[+] Add an item to a board" + Fore.RESET)
    add_parser.add_argument("item", help="the item you want to add", type=str, metavar="<item text>", nargs="+")
    add_parser.add_argument("-b", "--board", help="the board you want to add the item to (default: {})".format(DEFAULT_BOARD), type=str, metavar="<name>")
    add_parser.set_defaults(func=add)

    remove_parser = subparsers.add_parser("remove", help=get_color("remove") + "[-] Remove items" + Fore.RESET)
    remove_parser.add_argument("item", help="id of the item you want to remove", type=int, metavar="<item id>", nargs="+")
    remove_parser.set_defaults(func=remove)

    clear_parser = subparsers.add_parser("clear", help=get_color("clear") + "[x] Clear all items on a/all board(s)" + Fore.RESET)
    clear_parser.add_argument("board", help="clear this specific board", type=str, metavar="<name>", nargs="*")
    clear_parser.set_defaults(func=clear)

    tick_parser = subparsers.add_parser("tick", help=get_color("tick") + "[✓] Tick/Untick an item" + Fore.RESET)
    tick_parser.add_argument("item", help="id of the item you want to tick/untick", type=int, metavar="<item id>", nargs="+")
    tick_parser.set_defaults(func=tick)

    mark_parser = subparsers.add_parser("mark", help=get_color("mark") + "[*] Mark/Unmark an item" + Fore.RESET)
    mark_parser.add_argument("item", help="id of the item you want to mark/unmark", type=int, metavar="<item id>", nargs="+")
    mark_parser.set_defaults(func=mark)

    star_parser = subparsers.add_parser("star", help=get_color("star") + "[⭑] Star/Unstar an item" + Fore.RESET)
    star_parser.add_argument("item", help="id of the item you want to star/unstar", type=int, metavar="<item id>", nargs="+")
    star_parser.set_defaults(func=star)

    edit_parser = subparsers.add_parser("edit", help=get_color("edit") + "[~] Edit the text of an item" + Fore.RESET)
    edit_parser.add_argument("item", help="id of the item you want to edit", type=int, metavar="<item id>")
    edit_parser.add_argument("text", help="new text to replace the old one", type=str, metavar="<new text>")
    edit_parser.set_defaults(func=edit)

    tag_parser = subparsers.add_parser("tag", help=get_color("tag") + "[#] Tag an item with text" + Fore.RESET)
    tag_parser.add_argument("item", help="id of the item you want to tag", type=int, metavar="<item id>", nargs="+")
    tag_parser.add_argument("-t", "--text", help="text of tag (do not specify this argument to untag)", type=str, metavar="<tag text>")
    tag_parser.add_argument("-c", "--color", help="set the background color of the tag (default: {})".format(TAGS["default"]), type=str, metavar="<background color>")
    tag_parser.set_defaults(func=tag)

    due_parser = subparsers.add_parser("due", help=get_color("due") + "[:] Assign a due date to an item" + Fore.RESET)
    due_parser.add_argument("item", help="id of the item", type=int, metavar="<item id>", nargs="+")
    due_parser.add_argument("-d", "--date", help="due date of the item in the format of `<digit><d|w>` e.g. '1w4d' for 1 week and 4 days (11 days)", type=str, metavar="<due date>")
    due_parser.set_defaults(func=due)

    run_parser = subparsers.add_parser("run", help=get_color("run") + "[>] Run an item as command" + Fore.RESET)
    run_parser.add_argument("item", help="id of the item you want to run", type=int, metavar="<item id>")
    run_parser.set_defaults(func=run)

    move_parser = subparsers.add_parser("move", help=get_color("move") + "[&] Move an item to another board" + Fore.RESET)
    move_parser.add_argument("item", help="id of the item you want to move", type=int, metavar="<item id>", nargs="+")
    move_parser.add_argument("board", help="name of the destination board", type=str, metavar="<name>")
    move_parser.set_defaults(func=move)

    rename_parser = subparsers.add_parser("rename", help=get_color("rename") + "[~] Rename the name of the board" + Fore.RESET)
    rename_parser.add_argument("board", help="name of the board you want to rename", type=str, metavar="<name>")
    rename_parser.add_argument("new", help="new name to replace the old one", type=str, metavar="<new name>")
    rename_parser.set_defaults(func=rename)

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
    if args.i:
        if PPT is False:
            print(Style.BRIGHT + Fore.RED + "ERROR:", Fore.YELLOW + "Looks like you don't have 'prompt toolkit' installed. Therefore, you will not be able to use interactive mode.")
            print("You can install it with `pip3 install prompt_toolkit`.")
        else:
            try:
                InteractivePrompt().cmdloop()
            except KeyboardInterrupt:
                pass
    else:
        try:
            args.func
        except AttributeError:
            with Storage() as s:
                shelf = dict(s.shelf)
            if args.s:
                for board in shelf:
                    shelf[board] = sorted(shelf[board], key=lambda x: x["text"].lower())
            elif args.d:
                for board in shelf:
                    shelf[board] = sorted(shelf[board], key=lambda x: x["time"], reverse=True)
            if args.t:
                data = {}
                for board in shelf:
                    for item in shelf[board]:
                        if item["date"]:
                            if item["date"] not in data:
                                data[item["date"]] = []
                            item.update({"board": board})
                            data[item["date"]].append(item)
                shelf = data
            display_board(shelf, date=args.d, timeline=args.t)
        else:
            try:
                args.func(args)
            except NoteboardException as e:
                print(Style.BRIGHT + Fore.RED + "ERROR:", str(e))
                logger.debug("ERROR:", exc_info=True)
            except Exception:
                exc = sys.exc_info()
                exc = traceback.format_exception(*exc)
                print(Style.BRIGHT + Fore.RED + "Uncaught Exception:\n", *exc)
                logger.debug("Uncaught Exception:", exc_info=True)
    deinit()
