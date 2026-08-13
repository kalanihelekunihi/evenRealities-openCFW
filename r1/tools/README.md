# R1 tools

The R1 evidence toolchain: the scripts that pin recovered behavior to the stock
image, the models that check it, and the gates that keep the documentation
honest. Same convention as [`../../g2/tools/`](../../g2/tools) — entry points at
the top, everything else named by what it analyzes.

## Entry points

| Script | What it does |
| --- | --- |
| [`verify_openr1.py`](verify_openr1.py) | the full evidence gate — capability ledger, source ownership, every per-subsystem summary, and the host/sanitizer/ARM builds. `make -C r1 verify` |
| [`build_r1_source_ownership.py`](build_r1_source_ownership.py) | regenerate the function-ownership records; `--check` fails if they are stale |
| [`verify_r1_surface_coverage.py`](verify_r1_surface_coverage.py) | check the capability ledger against the recovered surface |
| [`verify_r1_decompilation.py`](verify_r1_decompilation.py) | authenticate the decompilation corpus |
| [`openr1_sim.c`](openr1_sim.c) | the host protocol/device simulator (`make -C r1 sim`) |
| [`verify_sdk_image.py`](verify_sdk_image.py) | check a built nRF52840 image against the recovered layout |

## Evidence producers

Named by what they establish. All read the reconstructed images from
[`../research/decompilation/rebuild/`](../research/decompilation/rebuild) and
emit pinned JSON that a correlation document quotes.

| Family | Count | Purpose |
| --- | ---: | --- |
| `summarize_r1_*.py` | ~180 | pin one subsystem: exact addresses, sizes, record layouts, provider edges |
| `emulate_r1_*.py` | ~40 | executable models of recovered behavior, used as oracles |
| `analyze_r1_*.py`, `export_r1_*.py`, `build_r1_*.py` | few | corpus extraction and cross-cutting analysis |
| [`ghidra_scripts/`](ghidra_scripts) | 53 | Ghidra headless scripts for the nRF52840 target |

To find the script behind a claim, read the correlation document — each one ends
with the exact command that regenerates its numbers:

```sh
python3 tools/summarize_r1_bae8_event_router.py
```

Run them from the `r1/` directory.

## Prerequisites

Everything here needs the reconstructed images, which are built from byte arrays
you supply locally:

```sh
make -C research/decompilation/rebuild verify
```

See [`../research/decompilation/rebuild/PROVENANCE.md`](../research/decompilation/rebuild/PROVENANCE.md).
The R1 firmware itself builds and passes its full test suite without them.

## What is not here

Two scripts covering device-ownership rekeying and signing were left out: they
belong to a separate owner-bootloader effort, not to the openR1 reconstruction,
and they depend on material outside this repository.
