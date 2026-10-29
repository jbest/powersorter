# powersorter

Scripts that sort digitized specimen images into a numbered folder tree on the
TORCH storage at TACC (Corral), generate web derivatives, and produce
URL-mapping CSVs for import into Symbiota.

See [NOTES.md](NOTES.md) for known issues, config clean-up, and ideas for
improvement.

## What it does

Given a "ready to sort" directory of files named by catalog number
(e.g. `BRIT1234.jpg`, `BRIT1234_med.jpg`, `BRIT1234_thumb.jpg`, `BRIT1234.dng`,
`BRIT1234_ocr.txt`), `process.py`:

1. Creates `_med` (900x900) and `_thumb` (390x390) JPEG derivatives next to each
   full-size JPG (skipped if they already exist, unless `--force`).
2. Moves every matching file to
   `<output_base_path>/<output_sub_path>/<prefix><folder number>/`, where the
   folder number is the catalog number rounded down to `folder_increment`
   and zero-padded to `number_pad`.
   `BRIT1234.jpg` becomes `.../web/BRIT/BRIT0001000/BRIT1234.jpg`.
3. Writes a CSV log of every move (who, what, result, source, destination).
4. Reads that log and writes `<log name>_urls.csv` with columns
   `catalog_number, large, web, thumbnail` for Symbiota's URL Mapping profile.

## Files

| File | Purpose |
|---|---|
| `process.py` | Main entry point: derivatives, sort, then URL file. Use this. |
| `powersorter.py` | Sorting engine (`sort`, `scan_files`, `move_file`, `build_regex`, `Settings`, `SortLogger`). Also runs standalone (sort only, no derivatives, no URLs). |
| `url_gen.py` | Builds the URL CSV from a sort log. Also runs standalone against an existing log. |
| `config_gen.py` | Prints an example v3 config JSON to stdout. |
| `image_resizer.py` | Older standalone resizer, superseded by `resize_image` in `process.py`. |
| `config/*.json` | One config per collection (see below). `config/old/` holds retired v1/v2 formats. |
| `tests/` | Unit tests (standard library `unittest`, no extra install): `python -m unittest discover tests` |
| `regex_notes.txt`, `gen_test_files.sh` | Scratch notes and a script to create test files in `./input_dir`. |

`old_powersort.py`, `powersorterCB.py`, `process_CB_old.py`, `process_new.py`,
`process_check.py`, `url_gen_*.py`, `proc_jb.py`, `ps_jb.py` and
`check_permissions.py` are untracked working copies, not part of the tracked tool.

## Requirements

- Python 3.9+ (tested on 3.9.21, the version on the TACC data node, and 3.12.3). The regex
  handling avoids a mid-pattern `(?i)`, which 3.11+ rejects.
- Pillow (`pip install pillow`), needed only by `process.py`
- Unix-like OS (`pwd` is used to record the username)

## Usage

```bash
# Always start with a dry run. It touches no files, but still writes a log.
python process.py -c config/BRIT_v3.json -n -v

# Real run, input directory taken from the config
python process.py -c config/BRIT_v3.json -v

# Override the input directory
python process.py -c config/BRIT_v3.json -i /path/to/batch -v

# Sort only, no derivatives
python process.py -c config/BRIT_v3.json -s

# Regenerate the URL file from an existing log
python url_gen.py -c config/BRIT_v3.json -i /path/to/log.csv
```

`process.py` options: `-c` config (required), `-i` input path override,
`-s` sort only, `-n` dry run, `-f` force overwrite (asks you to type
`overwrite`), `-v` verbose, `-d` debug.

Outputs:
- Sort log: `<log_directory_path>/<prefix>_<input dir name>_<timestamp>.csv`
  (with `_DRY-RUN` before `.csv` for dry runs)
- URL file: `<log file name>_urls.csv`, **written to the current working
  directory**, not the log directory.

## Config format (version 3.0)

```jsonc
{
  "versions": {"config_format": "3.0"},       // must be exactly "3.0"
  "collection": {
    "name": "BRIT",
    "prefix": "BRIT",                         // folder name prefix: BRIT0001000
    "catalog_number_regex": "(?P<catNum>(?P<instID>BRIT)(-(?P<collID>XX)-)*(?P<numerical>\\d+))",
    "web_base": "/corral-repl/projects/TORCH/web/",   // filesystem root served over HTTP
    "url_base": "https://web.corral.tacc.utexas.edu/torch/"
  },
  "files": {
    "folder_increment": 1000,                 // files per folder
    "number_pad": 7,                          // zero-padding of the folder number
    "log_directory_path": ".../archive/BRIT/logs/",
    "output_base_path": "/corral-repl/projects/TORCH/",
    "input_path": ".../staging/BRIT/ready_to_sort"
  },
  "file_types": {
    "web_jpg":       {"file_regex": "...", "output_sub_path": "web/BRIT/"},
    "web_jpg_med":   {...}, "web_jpg_thumb": {...},
    "archive_dng":   {"output_sub_path": "archive/BRIT/", ...},
    "ocr":           {...}
  }
}
```

Rules that the code relies on:

- The full match pattern is `(?i)` + `catalog_number_regex` + `file_regex`,
  applied with `re.match` to the bare file name (see `powersorter.build_regex`).
- `catalog_number_regex` **must** define the named groups `catNum` and
  `numerical`. `file_regex` may define `suffix`, `size` (`med`/`thumb`) and `ext`.
- `web_jpg`, `web_jpg_med` and `web_jpg_thumb` must all exist: `Settings.load_config`
  reads them unconditionally, and `url_gen` uses them to build URLs.
- The `file_types` key names matter: `url_gen` builds URLs only from the three
  `web_jpg*` types.
- `web_base` + `url_base` determine the URL. See NOTES.md about the trailing-slash
  trap before changing either.

## Running on TACC

Target layout on Corral (`/corral-repl/projects/TORCH/`):

```
staging/<COLL>/ready_to_sort/   input
web/<COLL>/<PREFIX>NNNNNNN/     jpg, _med, _thumb, ocr (served at url_base)
archive/<COLL>/<PREFIX>NNNNNNN/ dng
archive/<COLL>/logs/            sort logs
```

Before the first run for a collection, `web/<COLL>/`, `archive/<COLL>/` and
`archive/<COLL>/logs/` must already exist and be writable by the running user.
`process.py` exits if the log directory is not writable, and
`powersorter.sort` logs a failure and skips any file type whose output directory is
not writable. It creates the numbered subfolders itself.

Suggested workflow:

1. Copy the batch into `staging/<COLL>/ready_to_sort/`.
2. Run with `-n -v`. Check that matched counts and destinations look right.
3. Run for real. Keep the log and `_urls.csv`.
4. Spot-check a few URLs in a browser, then import the `_urls.csv` into Symbiota.

The tool has no TACC job-submission or scheduler integration. It runs
interactively on the login/data node.

## Adding a new collection

1. `python config_gen.py > config/NEW_v3.json` (or copy a similar config, e.g.
   `UTPB_v3.0.json`).
2. Set `name`, `prefix`, `catalog_number_regex`, `number_pad`, the three paths
   under `files`, and the `output_sub_path` values.
3. Create the `web/`, `archive/` and `logs/` directories on Corral.
4. Create a few test files (`gen_test_files.sh` is a template), then dry-run
   against them.
