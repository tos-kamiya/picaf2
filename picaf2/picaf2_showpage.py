from functools import lru_cache
import html
import os
import shlex
import sys
from typing import List, Tuple, Optional

import nicegui
from nicegui import ui


@lru_cache(maxsize=None)
def list_dirs_and_files(directory: str) -> Tuple[List[str], List[str]]:
    """
    Lists directories and files in the given directory and sorts them by length in descending order.

    Args:
        directory (str): The directory path from which to list directories and files.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists:
            - `dirs`: A list of directories sorted by length in descending order.
            - `files`: A list of files sorted by length in descending order.
    """
    if directory == "":
        directory = "/"
    dirs_and_files = os.listdir(directory)
    dirs = []
    files = []
    for f in dirs_and_files:
        full_path = os.path.join(directory, f)
        if os.path.isdir(full_path):
            dirs.append(f)
        else:
            files.append(f)
    dirs.sort(key=lambda name: len(name), reverse=True)
    files.sort(key=lambda name: len(name), reverse=True)
    return dirs, files


def real_path(path_parts: List[str], base_dir: str) -> str:
    """
    Converts a list of path parts to an absolute path.

    Args:
        path_parts (List[str]): A list representing the parts of the path.
        base_dir (str): The base directory to resolve the relative path against.

    Returns:
        str: The resolved absolute path.
    """
    if path_parts[0] == "":  # absolute path
        return "/".join(path_parts)
    else:
        # make it relative to the base dir
        return os.path.abspath(os.path.join(base_dir, *path_parts))


def path_check(path_like: str, base_dir: str) -> Optional[str]:
    """
    Checks if the given path or a similar path exists.

    Args:
        path_like (str): The path-like string to check.
        base_dir (str): The base directory to resolve relative paths.

    Returns:
        Optional[str]: The actual path if found, otherwise None.
    """
    parts = path_like.split('/')
    while len(parts) > 0 and parts != [""]:
        p = real_path(parts, base_dir)
        if os.path.exists(p):
            return "/".join(parts)
        else:
            last_part = parts.pop()
            if len(parts) > 0:
                directory = real_path(parts, base_dir)
                dirs, files = list_dirs_and_files(directory)
                for f in files:
                    if last_part.startswith(f):
                        return "/".join(parts + [f])
                for d in dirs:
                    if last_part.startswith(d):
                        return "/".join(parts + [d])
    return None


def extract_filenames(text: str, base_dir: str) -> List[Tuple[int, int, str]]:
    """
    Extracts filenames or path-like strings from the text and checks their existence.

    Args:
        text (str): The input text from which to extract file names or paths.
        base_dir (str): The base directory to resolve relative paths.

    Returns:
        List[Tuple[int, int, str]]: A list of tuples where each tuple contains:
            - The start index of the match in the text.
            - The end index of the match in the text.
            - The matched file or path string.
    """
    curdir_dirs, curdir_files = list_dirs_and_files(base_dir)

    found_path_poss = []

    # Check the presence of current directory files in the text
    for filename in curdir_files:
        pos = 0
        while pos < len(text):
            p = text.find(filename, pos)
            if p < 0:
                break  # while pos
            found_path_poss.append((p, p + len(filename), filename))
            pos = p + len(filename)

    # Check for directory-like patterns (e.g., "../", "./", "/")
    for d in curdir_dirs + ["../", "./", "/"]:
        pos = 0
        while pos < len(text):
            p = text.find(d, pos)
            if p < 0:
                break  # while pos

            if p > 0 and (d.startswith(".") or d.startswith("/")) and text[p - 1] == ".":
                pos += p + len(d)
                continue   # while pos

            q = text.find("\n", p + 1)
            if q < 0:
                q = len(text)
            path_like = text[p:q]

            path_exits = path_check(path_like, base_dir)
            if path_exits is not None:
                assert text[p:p + len(path_exits)] == path_exits
                found_path_poss.append((p, p + len(path_exits), path_exits))

            pos = p + len(d)

    # Sort by start index and filter out overlapping matches
    found_path_poss.sort(key=lambda d: (d[0], -d[1]))
    r = []
    done_pos = 0
    for fpp in found_path_poss:
        b, e, p = fpp
        if b >= done_pos:
            r.append(fpp)
            done_pos = e
    found_path_poss = r

    return found_path_poss


def setup_file_clickable_page(text, function_on_click):
    path_poss = extract_filenames(text, os.getcwd())

    nr_poss = []
    pos = 0
    while pos < len(text):
        i = text.find("\n", pos)
        if i < 0:
            break  # while pos
        nr_poss.append((i, i + 1, "\n"))
        pos = i + 1

    item_poss = path_poss + nr_poss
    item_poss.sort()

    text_segments = []
    if item_poss and item_poss[0][0] == 0:
        text_segments.append("")

    pos = 0
    while pos < len(text):
        if not item_poss:
            text_segments.append(text[pos:])
            break  # while pos
        b, e, _ = item_poss.pop(0)
        text_segments.append(text[pos:b])
        text_segments.append(text[b:e])
        pos  = e

    with nicegui.html.div().style("font-family: monospace; font-size: 12pt; margin: 0; padding: 0;"):
        segment_index = 0
        while segment_index < len(text_segments):
            with ui.row().style("font-family: monospace; font-size: 12pt; margin: 0; padding: 0;"):
                while segment_index < len(text_segments):
                    text = text_segments[segment_index]
                    is_special = segment_index % 2 == 1
                    segment_index += 1
                    if is_special:
                        if text == "\n":
                            break  # while segment_index
                        else:
                            ui.chip(text, on_click=lambda e: function_on_click(str(e.sender.text)), color="#eeeeee").props('square').style("font-family: monospace; font-size: 12pt; margin: 0; padding: 0 1;")
                    else:
                        text = html.escape(text).replace(" ", "&nbsp;")
                        ui.html(text).style("font-family: monospace; font-size: 12pt; margin: 0; padding: 0;")


input_text = os.environ.get("PICAF2_INPUT_TEXT")

if not input_text:
    sys.exit("Error: no PICAF2_INPUT_TEXT")

command = os.environ.get("PICAF2_COMMAND")
if command:
    def on_click(file_path):
        os.system(command.replace("{0}", shlex.quote(file_path)))
else:
    def on_click(file_path):
        print(shlex.quote(file_path))

# @ui.page('/',title='index')
# def index():
#     ui.button('close', on_click=lambda : ui.run_javascript('window.open(location.href, "_self", "");window.close()'))

setup_file_clickable_page(input_text, function_on_click=on_click)

ui.run(title="picaf2")

