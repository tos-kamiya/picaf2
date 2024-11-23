import argparse
import os
import subprocess
import sys

from .version import __version__

script_dir = os.path.dirname(os.path.realpath(__file__))


def main():
    parser = argparse.ArgumentParser(description='Show text as file-clickable page.')

    parser.add_argument('input_file', type=str, help='The input file including file paths.')
    parser.add_argument('-c', '--command', type=str, help='Command line for the clicked file. "{0}" as a place holder to put a file name.')
    parser.add_argument('-t', '--types', type=str, help='File type(s). "f": file, "d": directory, "fd": both file and directory.')
    parser.add_argument('-d', '--done-mark', action="store_true", help='Add check mark to the file name when clicked.')
    parser.add_argument("--version", action="version", version=__version__, help="Show the version number and exit.")

    args = parser.parse_args()

    if args.input_file == "-":
        text = sys.stdin.read()
    else:
        with open(args.input_file, 'r', encoding='utf8') as f:
            text = f.read()

    os.environ['PICAF2_INPUT_TEXT'] = text

    if args.command:
        os.environ['PICAF2_COMMAND'] = args.command

    if args.types:
        type_strs = "".join(sorted(set(args.types)))
        if type_strs not in ['f', 'd', 'df']:
            parser.error('Invalid --types value: {}'.format(args.types))
        os.environ['PICAF2_TYPES'] = type_strs

    os.environ['PICAF2_DONE_MARK'] = "1" if args.done_mark else "0"

    subprocess.run([sys.executable, os.path.join(script_dir, "picaf2_showpage.py")])


if __name__ == '__main__':
    main()

