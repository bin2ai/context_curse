import argparse
import curses
import json
from typing import List
from thing import Thing, ThingType


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Thank you for checking out Context Curser...\n a CLI tool for managing files and directories before feeding them into a LLM with a limited context window.")
    parser.add_argument('-e', '--extensions', type=str,
                        help='Comma-separated extensions to keep (e.g., "py,txt").')
    parser.add_argument('-i', '--input', type=str,
                        help='Path to JSON file with input preferences.')
    parser.add_argument('-o', '--output', type=str,
                        help='Path to output JSON file for saving selections.')
    return parser.parse_args()


def load_input_preferences(input_path: str) -> dict:
    """Load input preferences from a JSON file."""
    with open(input_path, 'r') as f:
        return json.load(f)


def curses_app(stdscr: 'curses.window', root: Thing, output_path: str):
    curses.curs_set(0)
    current_thing = root
    selected_index = 0
    expanded_dirs = set()  # Track which directories are expanded

    def get_visible_things() -> List[Thing]:
        """Get a list of visible things based on the expanded state."""
        visible = []

        def add_visible_children(thing: Thing, depth: int):
            visible.append((thing, depth))
            if thing.get_path() in expanded_dirs and thing.is_directory():
                for child in thing.get_children():
                    add_visible_children(child, depth + 1)

        add_visible_children(current_thing, 0)
        return visible

    def render():
        stdscr.clear()
        things_to_display: List[Thing] = get_visible_things()

        for idx, (thing, depth) in enumerate(things_to_display):
            thing: Thing
            depth: int
            # highlight the selected item
            if idx == selected_index:
                mark = ">"
            else:
                mark = ""

            if thing.is_directory():
                suffix = "\\"
            else:
                suffix = ""

            if thing.get_keep() and thing.get_children_keep():
                c = 2
            elif thing.get_keep() is None:
                c = 3
            else:
                c = 1

            color_pair = curses.color_pair(c)
            stdscr.attron(color_pair)
            # Add indentation based on the depth
            stdscr.addstr(
                idx, 0, f"{mark}{'    ' * depth}{thing.get_path()}{suffix}")
            stdscr.attroff(color_pair)

        stdscr.refresh()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Default
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Kept
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Mixed
    # Selected, not kept
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_GREEN,
                     curses.COLOR_WHITE)  # Selected, kept
    curses.init_pair(6, curses.COLOR_YELLOW,
                     curses.COLOR_WHITE)  # Selected, mixed

    while True:
        things_to_display: List[Thing] = get_visible_things()
        try:
            render()
        except curses.error:
            pass

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_index = max(0, selected_index - 1)
        elif key == curses.KEY_DOWN:
            selected_index = min(len(things_to_display) -
                                 1, selected_index + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            selected_thing: Thing = things_to_display[selected_index][0]
            selected_thing.set_keep(not selected_thing.get_keep())
        elif key == ord('s'):
            save_selections(root, output_path)
        elif key == ord('q') or key == ord('Q'):
            break
        elif key == ord(' '):  # Space bar toggles expansion/collapse
            selected_thing = things_to_display[selected_index][0]
            if selected_thing.is_directory():
                if selected_thing.get_path() in expanded_dirs:
                    expanded_dirs.remove(selected_thing.get_path())
                else:
                    expanded_dirs.add(selected_thing.get_path())
        try:
            render()
        except curses.error:
            pass


def save_selections(root: Thing, output_path: str):
    def serialize(thing: Thing):
        return {
            'path': thing.get_path(),
            'type': 'directory' if thing.get_type() == ThingType.DIRECTORY else 'file',
            'selected': thing.get_selected(),
            'children': [serialize(child) for child in thing.get_children()] if thing.get_children() else None
        }

    with open(output_path, 'w') as f:
        json.dump(serialize(root), f, indent=4)


if __name__ == '__main__':
    args: argparse.Namespace = parse_arguments()

    # Parse extensions
    file_extensions = args.extensions.split(',') if args.extensions else [
        'py']  # Default to .py files

    # Load input preferences if provided
    input_preferences = {}
    if args.input:
        input_preferences = load_input_preferences(args.input)

    # Start from the root path provided in input or current directory
    root_path = input_preferences.get('root_path', ".")
    root_thing = Thing(root_path, file_types=file_extensions)

    curses.wrapper(curses_app, root_thing,
                   args.output if args.output else 'selections.json')
