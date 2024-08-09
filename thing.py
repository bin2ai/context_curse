import enum
import os
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
