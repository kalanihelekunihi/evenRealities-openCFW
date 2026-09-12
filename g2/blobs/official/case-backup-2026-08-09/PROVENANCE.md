# Case backup supplementation, 2026-09-12

Confirmed locally: the 2026-08-09 case backup contains flash regions absent
from the archived case update components. No installed glasses flash dump was
found under the supplied webflasher repository. This archive supplements the
matching official releases with captured case data; it is a device-specific
reference/recovery archive, not an EVENOTA update or a validated flashing package.

## Inputs

- Backup: `/Users/kalani/Repo/sybilSight-webflasher/backups/JQU5-K2V8-2026-08-09.g2case-backup.json`
- Capture time: `2026-08-09T22:39:27.386Z`
- Flash: 524,288 bytes, SHA-256 `26e7941cdb1eaa1b6916f64ce66d2f50304d49a5f48d0bd2b46905d521b19746`
- Options: 128 bytes, SHA-256 `71649e18076587e422d82b31211ab1f1a90225420809d89afcfd296840ce3445`
- Official components: `firmware-archive/source-files/` and
  `public/firmware-updates/source-files/` in the same repository. Duplicate
  release mirrors must agree on source bundle SHA-256. Every copied component
  was checked against its metadata size and SHA-256; the case wrapper size,
  additive checksum and raw extraction were also verified.

## Findings

Addresses below are CPU aliases used by the capture, not physical-bank labels.
The original option bytes are separate at `0x1fff7800`; they must not be appended
to the flash address range or inferred from a bank filename.

| Captured alias range (end exclusive) | Captured contents | OTA comparison |
|---|---|---|
| `0x08000000–0x0800d9c8` | Case 1.2.57 application, 55,752 bytes | Exact official raw application match |
| `0x0800d9c8–0x0803f000` | Erased bytes | Omitted by OTA |
| `0x0803f000–0x08040000` | Two 2 KiB device-data pages | Omitted by OTA |
| `0x08040000–0x0804d8f8` | Case 1.2.56 application, 55,544 bytes | Exact official raw application match |
| `0x0804d8f8–0x0807f000` | Erased bytes | Omitted by OTA |
| `0x0807f000–0x08080000` | Two 2 KiB device-data pages | Omitted by OTA |

Each bank's first device-data page has 16 non-`ff` bytes; its second has 8.
Corresponding pages are identical between the banks. Thus the newly recovered
non-erased tail is device data, not additional executable code. The archive also
preserves the original two-version fallback-bank state and option data.

The webflasher's `src/lib/backup.js` explicitly sets
`smartGlassesInstalledMemoryReadback: false` and describes the glasses backup as
archived recovery bundles plus live identity snapshots. No new Apollo MRAM,
INFO0/INFOC, pairing-key or calibration coverage is established here.

## Combined artifacts

Each matching release directory contains its unchanged official component files,
the raw case application, and one 262,144-byte `case-merged-alias-*.bin` image.
The combined bank consists of the exact OTA raw application followed by the
captured tail from the matching bank. All combined banks equal their captured
bank byte for byte; no missing bytes were guessed. Glasses components remain
ordinary OTA components, not full-memory reconstructions.

| G2 release | Case version | Combined case alias |
|---|---|---|
| 2.1.1.12 | 1.2.56 | `0x08040000` |
| 2.2.0.24 | 1.2.57 | `0x08000000` |
| 2.2.4.34 | 1.2.57 | `0x08000000` |
| 2.2.6.10 | 1.2.57 | `0x08000000` |
| 2.2.7.14 | 1.2.57 | `0x08000000` |
| 2.2.8.4 | 1.2.57 | `0x08000000` |
| 2.2.9.22 | 1.2.57 | `0x08000000` |
| 2.2.10.10 | 1.2.57 | `0x08000000` |

Eight earlier official releases with case 1.2.40, 1.2.51 or 1.2.54 had no exact
application match and were not merged. Their entries and all output hashes are
in `manifest.json`.

`case-captured-flash.bin` preserves the full original 512 KiB capture;
`case-captured-options.bin` preserves the original 128 option bytes. These are
specific to the backed-up case. OTA bundles, existing canonical blobs and the
source backup were not changed. No hardware writes or boot validation occurred.
Binary outputs and the generated manifest remain ignored under the repository's
existing official-blob policy. This provenance and the reproducible tool are
source records, not a grant to redistribute vendor firmware or device data.

## Reproduce and verify

From the openCFW repository root:

```sh
python3 g2/tools/merge_case_backup.py \
  --source /Users/kalani/Repo/sybilSight-webflasher \
  --backup /Users/kalani/Repo/sybilSight-webflasher/backups/JQU5-K2V8-2026-08-09.g2case-backup.json \
  --output g2/blobs/official/case-backup-2026-08-09
python3 -m unittest discover -s g2/tests -p test_merge_case_backup.py
```

Five tests passed, covering preserved data, application mismatch, unexplained
non-erased tails, data-page overlap and refusal to overwrite different outputs.
An independent verification read all 64 output binaries, checked their sizes and
SHA-256 values, and compared every merged bank with the original capture and OTA
application. The generator also permits an identical rerun without overwriting
changed files.
