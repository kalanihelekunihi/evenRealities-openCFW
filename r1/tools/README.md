# R1 tools

The R1 evidence toolchain: the scripts that pin recovered behavior to the stock
image, the models that check it, and the gates that keep the documentation
honest.

## Entry points

| Script | What it does |
| --- | --- |
| [`verify_openr1.py`](verify_openr1.py) | **the gate** — capability ledger, source ownership, every subsystem summary, and the host/sanitizer/ARM builds. `make -C r1 verify` |
| [`build_r1_source_ownership.py`](build_r1_source_ownership.py) | regenerate the function-ownership records; `--check` fails if they are stale |
| [`verify_r1_decompilation.py`](verify_r1_decompilation.py) | authenticate the decompilation corpus |
| [`verify_r1_bootloader_reconstruction.py`](verify_r1_bootloader_reconstruction.py) | authenticate the bootloader reconstruction |
| [`verify_sdk_image.py`](verify_sdk_image.py) | check a built nRF52840 image against the recovered layout |
| [`export_r1_decompilation.py`](export_r1_decompilation.py) | regenerate the decompilation corpus |
| `run_r1_*.sh` | headless-Ghidra drivers for decompilation and BSim correlation |
| [`openr1_sim.c`](openr1_sim.c) | the host protocol/device simulator (`make -C r1 sim`) |

## `evidence/` — 197 scripts

Where a claim comes from. Each one reads the reconstructed image, proves
something about one subsystem, and emits pinned JSON that a correlation document
quotes.

| Family | Count | Purpose |
| --- | ---: | --- |
| `summarize_r1_*` | ~150 | pin one subsystem: exact addresses, sizes, record layouts, provider edges |
| `emulate_r1_*` | ~45 | executable models of recovered behavior, used as oracles |
| `analyze_r1_*`, `build_r1_227_*` | 2 | cross-cutting analysis and probe construction |

They import each other by bare module name, so they live in one directory. The
entry points above put `evidence/` on `sys.path`; running a script directly
works because Python adds its own directory.

Every correlation document ends with the command that regenerates its numbers:

```sh
cd r1 && python3 tools/evidence/summarize_r1_bae8_event_router.py
```

## `probes/` — 21 assets

On-device runtime probes: Cortex-M assembly (`r1_227_*.S`) that dumps
bootloader, UICR, APPROTECT, NFCT, and ST25 state from a running device, plus
one DFU decode audit in C. These are inputs to physical validation, not part of
any build.

## `ghidra_scripts/` — 53 scripts

Ghidra headless scripts for the nRF52840 target: function seeding, boundary and
callsite evidence, BSim comparison, and whole-image export.

## Prerequisites

Everything here needs the reconstructed images, built from byte arrays you
supply locally:

```sh
make -C r1/research/decompilation/rebuild verify
```

See [`../research/decompilation/rebuild/PROVENANCE.md`](../research/decompilation/rebuild/PROVENANCE.md).
The R1 firmware itself builds and passes its full test suite without them.

## Scope

This is a firmware repository. Scripts that audited the companion phone
application — its decompiled Dart AOT and Swift protocol controllers — are not
here: they analyze a different product and cannot run against this tree. The
firmware-side evidence they cross-checked is covered by the correlation records
under [`../docs/correlation/`](../docs/correlation).

Two device-ownership scripts (bootloader rekeying and signing) are also absent;
they belong to a separate owner-bootloader effort.
