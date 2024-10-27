import argparse
import os
import subprocess
import sys


script_dir = os.path.dirname(os.path.realpath(__file__))


def main():
    parser = argparse.ArgumentParser(description='Show text as file-clickable page.')

    parser.add_argument('input_file', type=str, help='The input file including file paths.')
    parser.add_argument('-c', '--command', type=str, help='The command applied when file clicked')
    parser.add_argument('--version', action='version', version='picaf2 1.0')

    args = parser.parse_args()

    if args.input_file == "-":
        text = sys.stdin.read()
    else:
        with open(args.input_file, 'r', encoding='utf8') as f:
            text = f.read()

    os.environ['PICAF2_INPUT_TEXT'] = text

    if args.command:
        os.environ['PICAF2_COMMAND'] = args.command

    subprocess.run([sys.executable, os.path.join(script_dir, "picaf2_showpage.py")])


if __name__ == '__main__':
    main()

