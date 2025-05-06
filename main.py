#!/usr/bin/env python
import argparse
from pathlib import Path

__TITLE__ = "Music Organizer"

def load_library_manifest():
    with open(Path.home / "Music" / ".libman"):
        pass

def main(parser=argparse.ArgumentParser()):
    print(__TITLE__)

    
    args = parser.parse_args()

if __name__ == "__main__":
    main()
