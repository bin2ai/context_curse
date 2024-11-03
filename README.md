# Context Curse

Context Curse is a command-line tool designed to manage files and directories, specifically for preparing data before feeding it into a language model (LLM) with a limited context window. It provides a terminal-based interface for selecting and managing files and directories.

## Features

Navigation: Navigate through directories and files.
Selection: Select or deselect files and directories.
Expansion/Collapse: Expand or collapse directories to view or hide their contents.
Save Selections: Save selected files and directories to a specified output file.
Massive File Generation: Generate a comprehensive file combining the contents of selected files and directories.

## Installation

You can install Context Curse using pip:

```bash
pip install context-curse
```

## Usage

After installation, you can run the context_curse command from your terminal. The available options are:

```bash
python -m context_curse -h
```

## Options

* -e, --extensions
  Comma-separated list of file extensions to keep (e.g., py,txt).

* -i, --input
  Path to a text file containing a list of paths to keep, one per line.

* -o, --output
  Path to the output text file where selected paths will be saved.

## Example

To run Context Curse with a specific configuration, use the following command:

```bash
python -m context_curse -e "py,txt" -i "preferences.txt" -o "preferences.txt"
```

the code above takes in the 'preferences.txt' file, which contains a list of paths to keep, and saves the selected paths to the same file.
the code also creates a 'preferences_massive.txt' file that contains the combined contents of the selected files and directories.

## Commands

While running Context Curse, use the following commands in the terminal interface:

* ↑/↓ : Navigate through items.
* Enter : Select or deselect the current item.
* Space : Expand or collapse directories.
* s : Save the current selections.
* q : Quit the application.

## Colors

* Green: Kept files or directories.
* Yellow: Mixed state (partially kept).
* White: Not kept files or directories.

## Contributing

Contributions to Context Curse are welcome. Please submit issues and pull requests on the GitHub repository.

## Acknowledgements

Context Curse utilizes the curses library for terminal-based UI and argparse for command-line argument parsing.

Feel free to adjust any sections or add additional details relevant to your project!
