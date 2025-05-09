# Music Organizer
A barebones CLI program to syncronize a local music library against a plaintext
manifest file.

By syncing this manifest file over git or cloud storage, you can keep identical
music libraries on different devices. With very little work, this could also be
used for digital archivism to prevent re-downloading videos.

```
usage: main.py [-h] [--config CONFIG] [-v] [--verbose-manifest] [-p]

options:
  -h, --help          show this help message and exit
  --config CONFIG     override the default config path
  -v, --verbose       print debugging information
  --verbose-manifest  display a parsed version of the library manifest
  -p, --pull-missing  populate missing songs in library
```
