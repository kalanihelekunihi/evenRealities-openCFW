# Apollo bootloader Ghidra decompilation harvest (XC-009)

Item: XC-009 (component cross-cutting, tooling). Scope: there was no
per-function decompilation corpus for the Apollo bootloader image — only
Apollo main (`research/corpus/apollo-main/ghidra/`), EM9305
(`research/corpus/em9305/ghidra/`), and the STM32 case
(`research/corpus/case/ghidra/`) had one. BL-* items had to disassemble the
raw bootloader blob address-by-address with no named, bounded functions to
anchor claims on. This item produces
`research/corpus/apollo-bootloader/ghidra/decomp/` with the existing generic
harvester, `tools/harvest_ghidra_decomp.py`, from a locally analyzed Ghidra
project — no new tooling capability, just a new target for it. This is
tooling/evidence only: it changes no production-routed bytes, no
manifest, and no component build.

## What was produced

A headless-Ghidra-analyzed project over the pinned official bootloader
payload, `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`
(SHA-256 `f89a4c46…4167b5`, 148,599 bytes), loaded at its documented flash
address `0x00410000` (`docs/memory-map.md`) with `ARM:LE:32:Cortex` /
`BinaryLoader`, using the same recipe `tools/run_apollo_ghidra_chunk_batch.sh`
already uses for Apollo main: `SeedCortexMVectorTable.java` disassembles
every distinct in-image vector target from the image's own Cortex-M vector
table (at its load address, not a separate header — the bootloader has no
Apollo-main-style pre-vector prologue) before full auto-analysis runs, so
the reset handler and every populated exception/IRQ vector starts out as a
named, bounded function rather than un-analyzed bytes.

`tools/harvest_ghidra_decomp.py --project-name apollo_bootloader_template
--program ota_s200_bootloader.bin` then exported every defined function's
decompiled C, bounds, signature, callees, and body SHA-256 through the
existing `ExportAllFunctionDecomp.java`/`ReportProgramCensus.java` scripts,
sharded across 4 workers, into the same deterministic
`functions.jsonl` + `bundles/*.c` + `HARVEST.json` + `SHA256SUMS` layout the
Apollo main corpus already uses. The harvest's own census records the
analyzed program's executable SHA-256, so a later re-harvest against a
stale or substituted project fails closed (`--expect-executable-sha256`).

## New tooling

`tools/ghidra_scripts/PadAddressSpace.java` is a new `-preScript` that
reserves additional uninitialized address space immediately after the
imported image, before analysis runs. Ghidra's raw `BinaryLoader` maps a
single memory block ending exactly at end-of-file; some functions' switch
statements make the decompiler speculatively probe an address just past the
last mapped byte while resolving jump-table bounds, which throws
`Low-level Error: Trying to construct memory range beyond end of address
space: ram` and is reported as a decompilation failure even though the
function's own body is fully defined and correctly bounded. Reserving spare
address space that is never given defined bytes (so it can never itself
contribute instructions or data) removes that artifact. A new
`g2/Makefile` target, `bootloader-ghidra-harvest`, documents the reusable
invocation the same way `transparent-harvest` does for Apollo main.

## Results

<!-- PLACEHOLDER: filled in from the final HARVEST.json census after the
     padded re-import; see docs/progress.md for the committed counts. -->

## What this is not

This is evidence, not source ownership. Every function in the corpus is
Ghidra decompiler output (`FUN_*` names, no symbols recovered) staged for
identification and source-recovery review; none of it is compiled,
reviewed, or production-routed. It supersedes nothing in
`docs/upstream-inventory.md` or `docs/memory-map.md` and performs no
hardware operation. Turning named, bounded entries into reviewed C for a
specific `BL-*` row is separate, per-row work — this item only removes the
"no corpus to anchor on" blocker those rows previously had.
