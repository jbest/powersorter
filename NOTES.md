# Notes for improving powersorter and the TORCH configs

Compiled 2026-10-29 from reading the code and every file in `config/`. Items marked
**(verified)** were reproduced by running the code; the rest come from reading it.
Within each section, items are ordered roughly by importance.

## 1. Bugs and sharp edges in the code

1. **Existing-file collisions are logged as `success`** (`powersorter.py`, `move_file`,
   the `destination.exists() and not force_overwrite` branch). The move fails
   (`status='fail'`) but the logger is called with `result='success'`. `url_gen` only
   keeps rows with `result == 'success'`, so a URL is emitted for the file that was
   not moved. Fix: log `result=status`. The dry-run branch does the same on purpose,
   with a comment ("to make url_gen work on dry run output"). If that is kept, record
   dry-run state in `action` and have `url_gen` filter on it instead of lying in `result`.
2. **`PermissionError`/other failures lose detail only partly**: they are logged, but
   `move_file` calls `sort_logger.log` unguarded while the dry-run branch guards
   `if sort_logger`. Pick one convention.
3. **`web_base` trailing slash changes the URLs (verified).** `url_gen.generate_url`
   takes `os.path.dirname(web_base)` as the root:

   | `web_base` | URL for `.../web/BRIT/BRIT0001000/BRIT1234.jpg` |
   |---|---|
   | `/corral-repl/projects/TORCH/web/` | `.../torch/BRIT/BRIT0001000/BRIT1234.jpg` (correct) |
   | `/corral-repl/projects/TORCH/web/BRIT` | same (correct) |
   | `/corral-repl/projects/TORCH/web/BRIT/` | `.../torch/BRIT0001000/BRIT1234.jpg` (**missing `BRIT/`**) |

   `HSU.json`, `HSU2.json` and `BRIT_v3_TACC.json` use the third form. Either fix
   `generate_url` to compute the path relative to `web_base` itself (stripping the
   trailing slash), or normalize all configs to `.../web/`. Doing both is best.
4. **`file_regex` is not anchored at the end** (verified): `re.match` anchors only the
   start, so `BRIT123.jpgx` and `BRIT123.jpg.bak` match `web_jpg`. Add `$` to every
   `file_regex`, or use `re.fullmatch` in `scan_files` and `url_gen.match_pattern`.
5. **`suffix` regex differences are dangerous (verified).** Configs with
   `(?P<suffix>.+)` (`BRIT_v3_TACC.json`, `config_gen_v3.json`, and the
   `config_gen.py` template) make `BRIT123_med.jpg` and `BRIT123_thumb.jpg` match
   `web_jpg` as well, with suffix `med`/`thumb`. That makes the sort order of file types
   decide the outcome, and `process.py` would generate derivatives of derivatives.
   The `[a-z]|[0-9]` (single character) form in the other configs is safe. Standardize
   on it, or on `[a-z0-9]` which is equivalent but clearer.
6. **URL file goes to the current directory** (`process.py`, last lines; TODO already
   in the code). Write it to `log_directory_path`, and optionally copy it somewhere
   web-accessible.
7. **Derivatives are created inside the input directory before the sort**, so a failed
   sort leaves `_med`/`_thumb` files next to the originals. This is benign (re-runs skip
   existing files) but means "dry run" and "real run" see different inputs. Consider
   generating derivatives directly in the destination folder, or sorting first and
   deriving after.
8. **Derivative sizes are hard-coded** (`MEDIUM_SIZE`, `THUMBNAIL_SIZE`, `QUALITY` in
   `process.py`). Move them into an optional `derivatives` block in the config
   (with the current values as defaults).
9. **Only `web_jpg` makes derivatives**, but it also matches any case of `.JPG/.jpeg`.
   `resize_image` always writes `.jpg`, so a `BRIT1.JPEG` gets `BRIT1_med.jpg`. This is fine, but
   untested.
10. **`SortLogger` is a singleton that ignores later filenames** (`__init__` returns
    early once initialized). Harmless for one run per process; a trap for tests and
    for any code that processes several collections in one process.
11. **`os.walk` scans recursively and never excludes anything.** If `input_path` ever
    contains (or is above) an output directory, sorted files can be matched again.
    Consider refusing to run when the input path is inside `output_base_path/web` or
    `archive`.
12. **Duplicated settings code**: `Settings.load_config` exists in both
    `powersorter.py` and `url_gen.py`, `CONFIG_FORMAT_REQUIRED` is defined in two places,
    and the force-overwrite prompt is copy-pasted in two entry points.
    `url_gen` could simply import `powersorter.Settings`.
13. **Weak config validation**: a missing `web_jpg_med` key raises
    `AttributeError: 'NoneType' ...` from `load_config`. A missing `files.log_directory_path`
    fails at `Path(None)`. Validate and print the offending key and file name.
14. **No end-of-run summary of unmatched files.** Files in the input directory that match
    no pattern are silently ignored. Listing them (count + names) would catch
    misnamed files.
15. **Dry run does not test permissions** (existing TODO). It also writes a log file
    to `log_directory_path`, so a dry run still needs a writable log directory.
16. **No tests.** The pure functions (`build_regex`, `scan_files`, folder-number
    arithmetic, `generate_url`) are easy to cover with pytest and a tmp dir.
    `regex_notes.txt` already lists good filename test strings (`BRIT1000.JPG`,
    `_med`, `_thumb`, `_ocr.json`, ...).
17. **Dead or stale code**: `image_resizer.py` (superseded by `process.py`),
    `url_gen.generate_url_records` (the pre-suffix version, which relies on globals),
    and the `-m/--med_tag`, `-t/--thumb_tag` options in `url_gen.py` that only the dead
    function uses.
18. **Repo hygiene**: `git status` shows many untracked CSVs, logs, tarballs, a
    `env/` virtualenv, `__pycache__/` and `.ipynb_checkpoints/`. Add a `.gitignore`
    (`env/`, `__pycache__/`, `*.csv`, `*.tar.gz`, `.ipynb_checkpoints/`, local input
    dirs) and move the experimental `*_old.py` / `*_CB*.py` / `*_jb.py` copies into
    `archive/` or delete them.

## 2. Config clean-up

> **Update 2026-10-29:** `config/` was renamed to `config_local_old/` and a new `config/`
> now mirrors the TACC server (see section 7). The table below describes the old
> directory, so every file name in it now lives in `config_local_old/`.

State of the old config directory (all are format `3.0`):

| Issue | Files |
|---|---|
| `web_base` has trailing slash **and** includes the collection (URL bug, see 1.3) | `BRIT_v3_TACC`, `HSU`, `HSU2` |
| `web_base` is the bare `web/` root (correct form) | `BRIT_v3`, `UTPB_v3.0`, `DUR`, `NOSU`, `OCLA`, `OCU`, `OKL`, `OKLA`, `UOBS`, `WABA`, `WOH`, `TTC` |
| `web_base` is the collection directory without slash (works, form differs) | `BRIT_v3.1`, `BRIT_v3_mac_local`, `LLC_v3`, `SRSC_v3`, `WBU_*` |
| `web_base` missing entirely (URL generation will fail) | `config_gen_v3.json` |
| `suffix` is `.+` (see 1.5) | `BRIT_v3_TACC`, `config_gen_v3`, and the `config_gen.py` template |
| Inline `(?i)` still present (harmless now, `build_regex` strips it) | `BRIT_v3`, `HSU`, `OKLA_v3` |
| Leftover `web_base_OLD` key (ignored by the code) | `BRIT_v3` |
| `prefix` is empty | `JAUM_v3`, `JAUM_v3_local`, `LLC_v3_mac_local` |
| `prefix` copied from another collection | `SRSC_v3` (prefix `LLC`, input `staging/LLC/`, logs `archive/LLC/`) |
| Paths under `/corral-repl/projects/BRIT/` rather than `.../TORCH/` | `JAUM_v3`, `JAUM_v3_local` |
| Machine-specific local paths (`/Users/jbest/...`, `/media/jbest/...`) | `BRIT_v3_mac_local`, `BRIT_v3_BDI_local`, `JAUM_v3_local`, `LLC_v3_mac_local` |
| Duplicate/near-duplicate versions | `BRIT_v3`, `BRIT_v3.1`, `BRIT_v3_TACC`; `HSU`, `HSU2`; `WBU_v3`, `WBU_vascular_v3` (identical prefix/pad) |

Suggested steps:

1. **Decide the canonical TACC config per collection** and delete or move the rest to
   `config/old/`. `BRIT_v3.json`, `HSU.json`, `OKLA_v3.json`, `UOBS_v3.json` and
   `config_gen.py` were deliberately synced to the TACC server copies in commit `8baf0e8`,
   so treat those server copies as the source of truth. The one exception is
   `WBU_v3.json`, where the server copy is the broken one (see section 7).
2. **Standardize on `web_base: ".../web/"`** and `suffix` = `[a-z]|[0-9]`.
3. **Check `number_pad` against each collection's real folder names on Corral.**
   Existing values differ (WBU 5, TTC 6, LLC/SRSC 8, others 7). A mismatch silently
   creates a second, parallel set of folders. This cannot be determined from the repo,
   so check each collection's `web/<COLL>/` listing.
4. **Check `catalog_number_regex` per collection** against real file names. `config_gen.py`
   hardcodes `BRIT`/`L` in the template regex even though the collection is `TEST`.
5. **Separate local and server configs**: use `config/local/` (gitignored) for
   machine-specific paths, and keep `config/` for TACC-valid ones.
6. Consider **inheriting from a shared base** (a `config/base.json` holding the common
   `file_types` and TORCH paths, plus a small per-collection file with only
   `name`, `prefix`, `catalog_number_regex`, `number_pad`, `input_path`). Right now every
   fix (such as commit `44ae309`) has to be repeated across 14+ files.
7. Add a **config validator** (`python config_check.py config/X.json`) that checks the
   format version, required keys, that regexes compile, that `catNum`/`numerical`
   groups exist, that `web_base` is a prefix of every web `output_sub_path`, and
   optionally that the paths exist and are writable. Run it against all configs in CI
   or as a pre-commit hook.
8. Give configs a **self-test**: a list of sample file names with the expected file
   type and destination folder, executed by the validator.

## 3. TACC / TORCH specifics worth deciding

- **Keep the path in one place.** `/corral-repl/projects/TORCH/` appears in every
  config. A single `torch_root` setting (or an environment variable) would make
  moving projects or testing a copy easy. `JAUM` already lives under
  `/corral-repl/projects/BRIT/`, which is evidence that paths do change.
- **Python on TACC**: the code runs on 3.9+ (tested, see section 7). Record how it is provided on the
  data node (module, conda env, venv) and add a `requirements.txt` (Pillow). Not
  captured in the repo yet.
- **Permissions and group ownership**: moved files keep the owner and mode of whoever
  ran the script. Decide on a umask/group (for example `g+rw`, group `TORCH`) so a
  later run by another user can overwrite or add to the same folders. `check_permissions.py`
  (untracked) looks like an early attempt at this and could be folded into the dry run.
- **`shutil.move` across filesystems copies then deletes.** On Corral staging→web it is
  a rename (same filesystem) and fast, but a copy plus delete if staging is ever on another
  mount, so failures can leave partial files. Optionally verify size or checksum after a
  cross-device move.
- **Logs are the only record.** Keep the sort logs and `_urls.csv` together under
  `archive/<COLL>/logs/` so a batch can be audited or reverted (a reverse-move
  script driven by a log file is a small, valuable addition, since the log has source
  and destination for every move).
- **Large batches**: scanning is single-threaded and `process.py` re-walks the input
  directory once per file type (five full walks). For big batches, walk once and
  classify each file against all patterns.
- **Derivative generation on the login node** can be slow and may be discouraged
  for heavy jobs. For large batches consider a SLURM batch script that wraps
  `process.py`, or `-s` (sort only) with derivatives produced elsewhere.
- **Web visibility**: confirm that everything under `web/` is meant to be public
  (`ocr` files go there too) and that `archive/` is not exposed.
- **Symbiota import**: `_urls.csv` columns are `catalog_number, large, web, thumbnail`.
  Document the exact import profile/field mapping the TORCH curators use, and how
  suffixed images (`BRIT123_a.jpg`) are meant to appear, since `url_gen` creates a
  separate row (same `catalog_number`) per suffix.

## 4. Suggested order of work

1. Fix 1.1 (success logged on failed move), 1.3 (trailing slash) and 1.4 (anchor
   regex); these affect data correctness.
2. Fix 1.5 and the config inconsistencies in section 2 (steps 1-4).
3. Write `config_check.py` and a small pytest suite, then run both on every config.
4. Add `.gitignore`, `requirements.txt`, clean up the untracked scripts.
5. Move URL output to the log directory, add the unmatched-files report, add the
   log-driven undo script.
6. Refactor: shared `Settings`, single directory walk, config inheritance.

## 5. Handoff: state as of 2026-10-29 and next session checklist

### State of the repo
- `main` is at `3d6c8d1` (docs) on top of `8baf0e8`, which synced `config_gen.py`,
  `BRIT_v3.json`, `HSU.json`, `OKLA_v3.json` and `UOBS_v3.json` to the TACC copies in
  `/corral-repl/projects/TORCH/tools` (on `data.tacc.utexas.edu`).
- No code fixes from section 1 have been made yet. The only code changes so far are
  `5a57d0b` (`build_regex`, dry-run and standalone bugs) and the regex fixes in `44ae309`.
- ~~`WBU_v3.json` differs from the server copy on purpose.~~ Corrected 2026-10-29: the
  server copy is stale and broken, not a deliberate difference (see section 7).
- Everything marked untracked in `git status` (CSV outputs, `env/`, `archive/`, `web/`,
  `input_dir/`, `*_old.py`, `*CB*.py`, `*_jb.py`, `url_gen_latest.py`, `url_gen_uknown.py`,
  `url_gen_old.py`, `check_permissions.py`, `config/WBU_v3_test.json`,
  `powersorter_update_2026-10-22.tar.gz`) exists only on the original laptop. Not reviewed
  in detail. Check what the tarball and `url_gen_latest.py` / `url_gen_uknown.py` contain
  before deleting anything, since they may be snapshots of server code.

### Things to read off the TACC server (not derivable from this repo)
Run these on `data.tacc.utexas.edu` and record the results in this file:

```bash
cd /corral-repl/projects/TORCH/tools
ls -la . config 2>/dev/null           # which scripts/configs are deployed
python3 --version; which python3      # 3.9+ is enough (see section 7)
python3 -c "import PIL; print(PIL.__version__)"

# number_pad per collection (NOTES 2, step 3): folder names should show the real padding
for c in /corral-repl/projects/TORCH/web/*/; do echo "$c"; ls "$c" | head -3; done

# directories each config needs, with owner/group/mode
ls -ld /corral-repl/projects/TORCH/{web,archive,staging}/*/ \
       /corral-repl/projects/TORCH/archive/*/logs
```

Compare every file in `config/` with the server copy, for example
`diff -r <repo>/config /corral-repl/projects/TORCH/tools/config`, and sort the
differences into: only in repo, only on server, differs. Decide the canonical set
(NOTES section 2, step 1) before editing configs.

### Suggested order
1. Data-correctness fixes: 1.1 (failed move logged as `success`), 1.3 (`web_base`
   trailing slash in `url_gen.generate_url`), 1.4 (anchor `file_regex`).
2. Standardize configs (section 2, steps 1-4), using the server facts above.
3. Add `config_check.py` and pytest tests, run against every config.
4. `.gitignore`, `requirements.txt`, remove or archive the stray scripts.

### Testing without touching real data
`gen_test_files.sh` creates sample files in `./input_dir`. Always dry-run first:
`python process.py -c config/<X>.json -n -v`. A dry run still writes a log to
`log_directory_path` and needs that directory to exist and be writable.
Remember to point `-i` at a scratch directory rather than the real `staging/` area when
experimenting on TACC.

## 6. Working on TACC from a Claude Code session (SSH control socket)

TACC logins need a password plus an MFA token, which Claude Code cannot type. Claude Code's
`!` shell has no terminal for prompts, so `ssh -fN` run there fails (it falls back to
`ssh-askpass` and gets `Permission denied`). Instead, the user opens one authenticated
connection in a separate terminal and Claude reuses it through an SSH control socket, so
there is no second MFA prompt. Validated 2026-10-29.

1. **In a separate terminal** (not the `!` prefix), log in and leave the session open:

   ```bash
   ssh -o ControlMaster=yes -o ControlPersist=2h \
       -o ControlPath=/tmp/tacc-cm.sock jbest@data.tacc.utexas.edu
   ```

2. **Claude runs commands through the socket**, each as a short-lived connection:

   ```bash
   ssh -o ControlPath=/tmp/tacc-cm.sock -o BatchMode=yes jbest@data.tacc.utexas.edu '<command>'
   rsync -av -e 'ssh -o ControlPath=/tmp/tacc-cm.sock' \
       jbest@data.tacc.utexas.edu:/corral-repl/projects/TORCH/tools/ <local scratch dir>/
   ```

   `BatchMode=yes` makes a command fail immediately if the socket is gone, rather than
   hanging on a prompt.
3. **Ground rules**: read-only on Corral unless the user says otherwise. Pull copies into a
   scratch directory outside the repo and diff them there.
4. **Lifetime**: the socket exists only while the terminal session is connected (and up to
   2 hours after it disconnects). Closing that terminal, or exiting the session, ends
   Claude's access. The socket carries the user's authenticated access, so anyone with
   access to `/tmp` on the machine could use it while open. Fine on a single-user laptop.
5. **Fallback without a socket**: the user runs
   `rsync -av jbest@data.tacc.utexas.edu:/corral-repl/projects/TORCH/tools/ <local dir>/`
   themselves, and Claude diffs the local copy.

## 7. Repo vs TACC comparison (2026-10-29)

Compared against `/corral-repl/projects/TORCH/tools` on `data.tacc.utexas.edu`
(read-only, via the SSH socket in section 6).

### Scripts: identical
`process.py`, `powersorter.py`, `url_gen.py` and `config_gen.py` are byte-identical to the
server copies. Server-only top-level files: `requirements.txt` (stale, lists `Wand==0.6.3`
although the code uses Pillow), `process_check.py`, `tacc_check.py`,
`tacc_check_suffix_test.py`, `tacc_fix.py`. Also on the server: `env/` (venv), `backup_2026-10-22/`,
`powersorter_update_2026-10-22.tar.gz`, many old `*_urls.csv` and `*_DRY-RUN*` outputs.

### Configs
The server has 26 top-level configs; the repo had 29. Of the overlap, 13 were identical
(`BRIT_v3`, `DUR_v3`, `HSU`, `NOSU_v3`, `OCLA_v3`, `OCU_v3`, `OKLA_v3`, `OKL_v3`, `TTC_v3`,
`UOBS_v3`, `UTPB_v3.0`, `WABA_v3`, `WOH_v3`) and one differed (`WBU_v3`).

- **Server-only (12):** `ACU_GCP_ingest`, `BCNWR_v3`, `CHIC_v3`, `SAT_v3`, `TAC`, `TAES_v3`,
  `TEST_v3`, `UTEP_GCP_ingest-TO-MODIFY`, `UTEP_TACC_staging-TO-MODIFY`, `UTPB_v3_WIP`,
  `VDB_v3`, `WBU-V_v3`.
- **Repo-only (14), now in `config_local_old/`:** `BRIT_v3.1`, `BRIT_v3_TACC`,
  `BRIT_v3_TACC_old`, `BRIT_v3_BDI_local`, `BRIT_v3_mac_local`, `OKLA_v3_local`, `HSU2`,
  `JAUM_v3`, `JAUM_v3_local`, `LLC_v3`, `LLC_v3_mac_local`, `SRSC_v3`, `WBU_vascular_v3`,
  `config_gen_v3`.

### WBU
The earlier note that `WBU_v3.json` differed from the server on purpose was wrong. The server
`WBU_v3.json` (2026-05-05) uses prefix `WBU` and the broken suffix group
`(?P<suffix>a-z|0-9)` (matches the literal text "a-z") with an inline `(?i)`. The server
`WBU-V_v3.json` (2026-08-07) has the same broken `file_regex` but a different, correct
`catalog_number_regex` (`(?P<instID>WBU-V-)(?P<numerical>\d+)`).

Decision: one WBU config only. The local `config/WBU_v3.json` takes the catalog regex from
`WBU-V_v3.json` and the fixed `file_regex` values (`[a-z]|[0-9]`, no inline `(?i)`) from
commit `44ae309`. `WBU-V_v3.json` was removed from the local `config/`. Tested against
`WBU-V-123.jpg`, `_a.jpg`, `_med.jpg`, `_a_med.jpg`, `_thumb.jpg`, `.dng`, `_ocr.txt`.

**Deployed 2026-10-29:** the new `WBU_v3.json` was copied to the server (checksum matches the
repo copy) and `WBU-V_v3.json` was removed from the server `config/`. Nothing on the server
referred to either by name. Both originals are in
`tools/backup_2026-10-29_wbu/`; roll back by copying them into `config/`. The server and
local `config/` now agree on WBU.

A dry run (`process.py -c config/WBU_v3.json -n -v`, using the real
`staging/WBU/ready_to_sort/`) exited 0 with 0 files matched. That is correct: the only files
there are 8 `WBU-V-0026x (2).JPG/.dng` files whose ` (2)` does not fit the pattern. They look
like duplicates of images already sorted on 2026-08-07. This run therefore proves the config
loads, not the regex; the regex was checked locally against sample names.

**Open on the server (not changed):**
- `web/WBU/WBU00000/` holds 3 files (`WBU-V-00001.jpg`, `_med`, `_thumb`) written on
  2026-05-05 by the old config (prefix `WBU`). The real folder is `web/WBU/WBU-V-00000/` (978
  files). Check whether the 3 files duplicate ones there, then remove the stray folder.
- Decide what to do with the 8 ` (2)` files in staging (compare with the sorted copies first).
- Stale WBU logs in `archive/WBU/logs/` use prefixes `WBU_` (old config) and `WBU-V_`.

### New layout
- `config/` mirrors the server's `tools/config/` exactly (45 files including `old/` and
  `HSU.json.bak`), except for the fixed `WBU_v3.json` and the removed `WBU-V_v3.json`.
- `config_local_old/` holds the previous repo `config/` (including the machine-specific
  `*_local` configs) so nothing is lost.

### Python on the server
System `python3` is 3.9.21 with no Pillow. `tools/env` is a venv (a symlink to the system
`/usr/bin/python3`, so also 3.9.21) with Pillow 11.3.0. No newer Python is installed on the
data node. The laptop's local `env/` is 3.12.3, which is probably where the old "3.11+" wording
came from.

**Tested 2026-10-29: the code works on 3.9.21.** `process.py -n -v` ran end to end on the
server with `tools/env/bin/python`. A separate test loaded every v3 config in `config/`
(21 configs, 105 regexes) and ran `build_regex` with `DeprecationWarning`/`FutureWarning`
raised as errors. All compiled, and 656 filename/config combinations (`.jpg`, `.JPG`,
`_med`, `_thumb`, `_a`, `.dng`, `_ocr.txt`, `.jpg.bak`) matched identically on 3.9.21 and
3.12.3. A mid-pattern `(?i)` compiles with a `DeprecationWarning` on 3.9 but is a hard
`re.error` on 3.12, which is why `build_regex` strips it. README now says 3.9+.

The same test confirmed two section 1 bugs against the server configs:
- **1.5:** `VDB_v3.json` uses the `.+` suffix, so `BRIT123_med.jpg` and `_thumb.jpg` also
  match `web_jpg`. It is the only config where this showed up.
- **1.4:** `X123.jpg.bak` matches in at least 14 of the 21 configs (the other 7 matched
  none of the sample names, so nothing can be said about them).
