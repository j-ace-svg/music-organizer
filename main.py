#!/usr/bin/env python
import argparse
import os
from pathlib import Path
import toml
import appdirs
import yt_dlp

__TITLE__ = "Music Organizer"

def dir_path(path):
    """
    Validate a CLI path argument
    """
    if os.path.isdir(path):
        return path
    else:
        raise NotADirectoryError(path)

def gen_config_schema():
    return {
        "library-path": {
            "type": Path,
            "default": Path.home() / "Music",
        },
        "manifest-path": {
            "type": Path,
            "default": Path.home() / "Music" / ".libman",
        },
        "yt-dlp": {
            "type": "optional",
            "default": {
                "quiet": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                    }
                ]
            },
        },
    }

def load_config(config_path = Path(appdirs.user_config_dir("music-organizer")) / "config.toml"):
    with open(config_path) as config_file:
        config_file_dict = toml.load(config_file)
        config_schema = gen_config_schema()
        full_config = {}

        def process_sublevel(full_config_category, config_schema_category, config_file_category):
            for key in set(config_file_category) | set(config_schema_category):
                if not key in config_schema_category:
                    raise AttributeError(key)

                if config_schema_category[key]["type"] == dict:
                    full_config_category[key] = {}
                    process_sublevel(full_config_category[key], config_schema_category[key]["value"], config_file_category[key])
                else:
                    if not key in config_file_category:
                        full_config_category[key] = config_schema_category[key]["default"]
                    elif config_schema_category[key]["type"] == Path:
                        full_config_category[key] = Path.expanduser(Path(config_file_category[key]))
                    else:
                        full_config_category[key] = config_file_category[key]

        process_sublevel(full_config, config_schema, config_file_dict)

        return full_config

def gen_youtube_downloader_outpath(config, path):
    yt_opts = config["yt-dlp"]
    yt_opts["outtmpl"] = str(path)

    downloader = yt_dlp.YoutubeDL(yt_opts)

    return downloader

def load_library_manifest(config):
    indent_size = 2

    with open(config["manifest-path"]) as manifest:
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

def pull_missing_songs(config):
    manifest = load_library_manifest(config)

    def process_sublevel(current_directory, path_prefix):
        for key in current_directory:
            subpath = path_prefix / key["name"]
            if key["directory"]:
                if not os.path.isdir(subpath):
                    os.mkdir(subpath)
                process_sublevel(key["value"], subpath)
            else:
                if not os.path.isfile(subpath):
                    downloader = gen_youtube_downloader_outpath(config, subpath)
                    downloader.download(key["value"])

    process_sublevel(manifest, config["library-path"])

def main(parser=argparse.ArgumentParser()):
    print(__TITLE__)

    parser.add_argument("--config", type=dir_path, help="override the default config path")
    parser.add_argument("--verbose-manifest", action="store_true", help="display a parsed version of the library manifest")
    parser.add_argument("--pull-missing", action="store_true", help="populate missing songs in library")
    args = parser.parse_args()

    if args.config:
        config = load_config(args.config)
    else:
        config = load_config()
    print(config)

    if args.verbose_manifest:
        print(load_library_manifest(config))

    if args.pull_missing:
        pull_missing_songs(config)

if __name__ == "__main__":
    main()
