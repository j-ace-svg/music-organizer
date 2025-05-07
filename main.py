#!/usr/bin/env python
import argparse
from pathlib import Path

__TITLE__ = "Music Organizer"

def load_library_manifest():
    indent_size = 2

    with open(Path.home() / "Music" / ".libman") as manifest:
        indent_level = 0
        current_line = manifest.readline()
        assert(current_line[:2] != "- ")

        def process_sublevel(current_line, indent_level):
            level_value = []
            while True:
                if not current_line:
                    break

                new_indent_level = (len(current_line) - len(current_line.lstrip())) / indent_size
                assert(new_indent_level == new_indent_level // 1)
                assert(new_indent_level <= indent_level + 1)
                assert(current_line.lstrip()[:2] == "- " or new_indent_level == 0)

                current_line_value = current_line.lstrip()[:-1]
                if current_line.lstrip()[:2] == "- ":
                    new_indent_level += 1
                    current_line_value = current_line_value[2:]

                if new_indent_level < indent_level:
                    break
                if new_indent_level > indent_level:
                    level_value[-1] = {
                        "directory": True,
                        "name":
                            level_value[-1]["value"] +
                            (" " + level_value[-1]["name"] if level_value[-1]["name"]
                             else ""),
                        "value": process_sublevel(current_line, indent_level + 1),
                    }
                else:
                    song = current_line_value.split(" ", 1)
                    if len(song) == 1:
                        song.append("")
                    level_value.append({
                        "directory": False,
                        "name": song[1],
                        "value": song[0],
                    })

                current_line = manifest.readline()
                indent_level = new_indent_level
            return level_value

        return process_sublevel(current_line, 0)

def main(parser=argparse.ArgumentParser()):
    print(__TITLE__)

    parser.add_argument("--verbose-manifest", action="store_true", help="display a parsed version of the library manifest")
    args = parser.parse_args()

    if args.verbose_manifest:
        print(load_library_manifest())

if __name__ == "__main__":
    main()
