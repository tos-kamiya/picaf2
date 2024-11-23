# picaf2

![](./images/picaf2-mascot-q.png)

`picaf2` (Pick-up a file) is a tool to generate a clickable map of files.

Show the window that allows you to click filenames, from text containing file names.

## Installation

```sh
pipx install git+https://github.com/tos-kamiya/picaf2
```

## Usage

```sh
picaf2 [options] inupt_file
```

Launch a web page showing text in the file as a map of clickable filenames.

By default, when a file name is clicked, print the filename. With the option `-c`, you can execute the specified command for the filename.

### Options

```
-c COMMAND, --command=COMMAND     Command line for the clicked file. `{0}` is a place holder to put a file name.
-t TYPES, --types=TYPES           File type(s). "f": file, "d": directory, "fd": both file and directory.
```

### Example of Use/Screenshots

**Ubuntu 24.04**

```sh
tree | picaf2 - -tf -c 'wc {0}'
```

![](./images/screenshot-ubuntu.png)

## Changelog

* v0.2.1 fix to recognize "~/" as a directory.
* v0.2.0 add `--done-mark' option for marking a file as done when clicked.
* v0.1.1 add `--types` option to specify file types.
* v0.1.0 the first release.
