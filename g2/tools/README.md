# G2 tools

This directory contains the G2 build, distribution, admission, and evidence
tools. Start with the workflow entry points below; the remaining scripts are
mostly narrowly named evidence producers.

## Entry points

These are the ones you invoke directly.

| Script | What it does |
| --- | --- |
| [`open_cfw.py`](open_cfw.py) | build, verify, and inspect a firmware package from a manifest — the packager behind `make reference` / `ring-source` / `source` |
| [`community_distribution.py`](community_distribution.py) | create, verify, locally hydrate, or smoke-test the official-payload-free public source ZIP; it never authorizes a hydrated tree or built firmware for redistribution |
| [`audit_g2_release_licensing.py`](audit_g2_release_licensing.py) | audit mixed-source licenses and fail closed on missing binary redistribution authority |
| [`release_cfw.py`](release_cfw.py) | produce the version-adjusted stock-bearing release artifact only after the internal authority gate passes; the current six-payload authority inventory deliberately blocks it |
| [`apply_g2_canonical_observations.py`](apply_g2_canonical_observations.py) | verify four independent Apollo-core observations and, only with `--apply`, transactionally admit reviewed pins |
| [`apollo_overlay.py`](apollo_overlay.py) | compile an Apollo source overlay from a component's `overlay.json` and place it byte-exactly |
| [`detect_toolchain.py`](detect_toolchain.py) | resolve the reviewed compiler profile for this host (`make toolchain` prints the result) |
| [`verify_research_corpus.py`](verify_research_corpus.py) | authenticate [`../research/`](../research) against its delivered manifests |
| [`harvest_ghidra_decomp.py`](harvest_ghidra_decomp.py) | export every function's decompilation from an analyzed Ghidra project (`make transparent-harvest`) |
| [`build_transparent_function_db.py`](build_transparent_function_db.py) | reconcile the harvest, the census, the function maps and the overlay into one address-keyed database (`make transparent-db`) |
| [`generate_transparent_source.py`](generate_transparent_source.py) | turn that database into a compilable C codebase (`make transparent-source`) |
| [`build_transparent_image.py`](build_transparent_image.py) | link the generated codebase into an Apollo image with no opaque spans (`make transparent-image`) |
| [`report_transparent_coverage.py`](report_transparent_coverage.py) | write the coverage ledger that separates recovered from declared from trapped (`make transparent-ledger`) |

The five `*transparent*`/function-database entries are the transparent-source
pipeline. What they establish, and what they deliberately do not, is in
[`../docs/transparent-source.md`](../docs/transparent-source.md).

`open_cfw.py` and `apollo_overlay.py` are pinned **by path** in the vendored
snapshots' production-exclusion gates. They cannot move.

## Analyzers — `analyze_*.py`

Analyzers are read-only by default: each reads evidence, proves something about
one subsystem, and returns or prints a report. Many have a matching
`tests/test_<name>.py` that pins the result. A bounded subset also exposes an
explicit `--write*` maintainer option for refreshing a checked manifest or
summary. Do not invoke a write option as an ordinary verification step; use the
corresponding Make target and review the resulting diff. No analyzer writes to
firmware or contacts hardware.

Naming is `analyze_<target>_<subsystem>.py`:

| Prefix | Count | Target |
| --- | ---: | --- |
| `analyze_g2_*` | 480 | the Apollo510 application, bootloader, Touch, and case |
| `analyze_em9305_*` | 14 | the EM9305 BLE controller image |
| `analyze_apollo_*` | 1 | Apollo-wide embedded source-path recovery |
| `analyze_gx8002_*` | 1 | the codec source-readiness boundary |

To find the analyzer for a subsystem, guess the name — `ls analyze_g2_cordio_*`,
`ls analyze_g2_service_*`, `ls analyze_g2_nanopb_*`. The subsystem vocabulary
matches [`../docs/source-coverage.md`](../docs/source-coverage.md).

## Other evidence producers

| Family | Scripts | Purpose |
| --- | --- | --- |
| `compare_em9305_*` | 4 | diff the EM9305 image against built SDK references |
| `emulate_*` | 4 | executable models used as oracles for recovered behavior |
| `recover_*`, `prove_*`, `disassemble_*` | 3 | targeted recovery and proof runs |
| `build_*`, `run_*`, `generate_*` | 3 | drive corpus generation (Ghidra chunks, SDK batches) |
| `*_audit.py`, `thumb_branch_audit.py` | 2 | standalone audits with their own pinned evidence |
| `benchmark_*` | 1 | measured comparisons |
| `unittest_identity_baseline.py` | 1 | compare test-suite identity across revisions |
| `verify_ambiqsuite_cordio_wsf_timer_archive.py` | 1 | authenticate one delivered archive |

## Data and scripts

| Path | Contents |
| --- | --- |
| [`manifests/`](manifests) | checked TSV/JSON evidence tables the analyzers read row-by-row — function maps, provenance, closures, readiness matrices |
| [`ghidra_scripts/`](ghidra_scripts) | Ghidra headless scripts for Thumb and ARCompact targets |
| [`patches/`](patches) | source patches applied to vendored upstreams |
| [`prompts/`](prompts) | recorded prompts for the analysis lanes |
| `*.sh` | 3 headless-Ghidra batch drivers |

## Why this is one flat directory

It reads like a directory that wants subdirectories. It resists them for two
reasons, both load-bearing:

1. **The analyzers import each other by bare module name** — 180 of them do.
   They have to stay co-located.
2. **Their paths and digests are pinned outside this directory.** The vendored
   snapshot verifiers record `(path, size, sha256)` triples for seven analyzers
   and for eleven `docs/research/` audits; those verifiers are themselves
   hash-pinned by the test suite. Adding a directory level to these paths means
   editing pinned evidence records and then re-pinning the hashes that exist to
   detect exactly that edit.

The convention does the work instead: start from the workflow table above;
everything matching `analyze_*` is read-only unless an explicit, documented
`--write*` option is requested. Navigate by name, not by directory.
