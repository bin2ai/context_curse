import curses
import enum
import os
import json
from typing import List


def get_paths(root: str, file_types: List[str], ignore: List[str] = []) -> List[str]:
    """Search through the root directory and return a list of all files with the given file types."""
    if not file_types:
        file_types = ['']

    paths = []
    for item in os.listdir(root):
        if item in ignore:
            continue
        full_path = os.path.join(root, item)
        if os.path.isdir(full_path):
            paths.append(full_path)
        else:
            if (file_ext := os.path.splitext(item)[-1].lstrip('.')) in file_types or file_types == ['']:
                paths.append(full_path)
    return paths


class ThingType(enum.Enum):
    FILE = 1
    DIRECTORY = 2


class Thing:
    def __init__(self, path: str, parent: 'Thing' = None, file_types: List[str] = [], ignore: List[str] = []):
        self.__path: str = path
        self.__parent: Thing = parent
        self.__children: List[Thing] = []
        self.__selected: bool = False
        self.__hidden: bool = False
        self.__keep: bool = False

        if self.is_directory():
            self.__type = ThingType.DIRECTORY
            for child_path in get_paths(self.__path, file_types, ignore):
                self.__children.append(Thing(child_path, self))
        else:
            self.__type = ThingType.FILE

    def get_path(self) -> str:
        return self.__path

    def get_type(self) -> ThingType:
        return self.__type

    def get_parent(self) -> 'Thing':
        return self.__parent

    def get_children(self) -> List['Thing']:
        return self.__children

    def get_selected(self) -> bool:
        return self.__selected

    def get_hidden(self) -> bool:
        return self.__hidden

    def get_keep(self) -> bool:
        return self.__keep

    def get_children_keep(self) -> bool:
        if not self.__children:
            return self.__keep
        return all([child.get_keep() for child in self.__children])

    def get_children_not_keep(self) -> bool:
        if not self.__children:
            return not self.__keep
        return all([not child.get_keep() for child in self.__children])

    def set_selected(self, selected: bool):
        self.__selected = selected

    def set_hidden(self, hidden: bool):
        self.__hidden = hidden

    def __set_keep_update_children(self, keep: bool):
        """ Recursively set the keep value for this item and all its children."""
        self.__keep = keep
        if self.__type == ThingType.DIRECTORY:
            for child in self.__children:
                child.__set_keep_update_children(keep)

    def __check_and_update_parent(self):
        """ Update the parent's keep value based on the children's states."""
        if self.__parent:
            all_kept = all(child.get_keep()
                           for child in self.__parent.get_children())
            none_kept = all(child.get_keep()
                            is False for child in self.__parent.get_children())

            if all_kept:
                self.__parent.__keep = True
            elif none_kept:
                self.__parent.__keep = False
            else:
                self.__parent.__keep = None

            # Recursively update the parent's keep state
            self.__parent.__check_and_update_parent()

    def set_keep(self, keep: bool):
        """Set the keep value and update children and parent accordingly."""
        self.__keep = keep
        self.__set_keep_update_children(keep)
        self.__check_and_update_parent()

    def is_directory(self) -> bool:
        return os.path.isdir(self.__path)

    def toggle_visibility(self):
        self.__hidden = not self.__hidden
        for child in self.__children:
            child.set_hidden(self.__hidden)


def curses_app(stdscr: 'curses.window', root: Thing):
    curses.curs_set(0)
    current_thing = root
    selected_index = 0
    expanded_dirs = set()  # Track which directories are expanded

    def get_visible_things() -> List[Thing]:
        """Get a list of visible things based on the expanded state."""
        visible = []

        def add_visible_children(thing: Thing):
            visible.append(thing)
            if thing.get_path() in expanded_dirs and thing.is_directory():
                for child in thing.get_children():
                    add_visible_children(child)

        add_visible_children(current_thing)
        return visible

    def render():
        stdscr.clear()
        things_to_display = get_visible_things()

        for idx, thing in enumerate(things_to_display):
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
            stdscr.addstr(idx, 0, f"{mark} {thing.get_path()}{suffix}")
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
        things_to_display = get_visible_things()
        render()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_index = max(0, selected_index - 1)
        elif key == curses.KEY_DOWN:
            selected_index = min(len(things_to_display) -
                                 1, selected_index + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            selected_thing = things_to_display[selected_index]
            selected_thing.set_keep(not selected_thing.get_keep())
        elif key == ord('s'):
            save_selections(root)
        elif key == ord('q') or key == ord('Q'):
            break
        elif key == curses.KEY_RIGHT:
            selected_thing = things_to_display[selected_index]
            if selected_thing.is_directory() and selected_thing.get_path() not in expanded_dirs:
                expanded_dirs.add(selected_thing.get_path())
        elif key == curses.KEY_LEFT:
            if selected_index > 0:
                selected_thing = things_to_display[selected_index]
                if selected_thing.get_path() in expanded_dirs:
                    expanded_dirs.remove(selected_thing.get_path())
                else:
                    parent = selected_thing.get_parent()
                    if parent:
                        selected_index = things_to_display.index(parent)
        elif key == ord(' '):  # Space bar toggles expansion/collapse
            selected_thing = things_to_display[selected_index]
            if selected_thing.is_directory():
                if selected_thing.get_path() in expanded_dirs:
                    expanded_dirs.remove(selected_thing.get_path())
                else:
                    expanded_dirs.add(selected_thing.get_path())

        render()


def save_selections(root: Thing):
    def serialize(thing: Thing):
        return {
            'path': thing.get_path(),
            'type': 'directory' if thing.get_type() == ThingType.DIRECTORY else 'file',
            'selected': thing.get_selected(),
            'children': [serialize(child) for child in thing.get_children()] if thing.get_children() else None
        }

    with open('selections.json', 'w') as f:
        json.dump(serialize(root), f, indent=4)


if __name__ == '__main__':
    root_path = "."  # Starting from the current directory
    root_thing = Thing(root_path, file_types=['py'])
    curses.wrapper(curses_app, root_thing)
