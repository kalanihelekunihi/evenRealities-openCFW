# Bounded ARM tool pass: main TLSF mapping attribution

The historically unverified TLSF candidate `0x004CFF6C–0x004CFF9A` is behaviorally identifiable as `mapping_insert` from the pinned TLSF v3.1 family. Its main-image geometry is `SL_INDEX_COUNT_LOG2=5`, `ALIGN_SIZE_LOG2=2`, `FL_INDEX_SHIFT=7`, `SMALL_BLOCK_SIZE=128`, and 32 second-level bins. This narrows a source attribution and configuration question; it does not establish the producing compiler, exact source revision, whole allocator correctness, or campaign acceptance.

## Scope and input authentication

Read active workflow README, PROCEDURE, CONTRACTS and REPOSITORY. Selected this distinct unresolved 46-byte body from `g2/symbols/apollo_main.tsv`; it carries an Unverified/link-order attribution. Independent historical body extent and SHA are in `g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl:3416`. Current bytes authenticate against full payload SHA `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` and body SHA `c1275ed4397a9e46d7c3fe8b57a6f7e434c5a4ac6764d3786235b05c6a401b79`.

The address map is payload offset = loaded address minus `0x00437FE0`; this function begins at payload offset `0x97F8C`. The private ELF in this directory maps the entire original main payload, preserving externally referenced bytes. Its authored executable section/symbol metadata are analysis aids and make no classification claim about every mapped byte. Symbol entry has the Thumb bit; Ablation's missing static-symbol Thumb state is supplied explicitly after checking the original instructions. No canonical writable project, source, gate or ledger is changed.

## Actual tool result and independent verification

`probe.py` uses installed Ablation `97e051b44d1ac8129b35556fe533e6e8b5338db2`, matching `third-party/tools/ablation`. It uses direct uncached `BinaryContext.build` and `FuncProfiler`, with no model, configuration or global-cache update. Profile finds precisely one call, `0x004CFF84 → 0x004CFD66`, agreeing with independent GNU force-Thumb disassembly. Profile arguments do not establish the ABI: its unknown r0 misses the instruction-proved `r0 = size`, and its nine apparent strings are printable instruction bytes, not proved string references. Full mapped context therefore does not repair this heuristic limitation.

GNU listing covers the complete 46-byte body, its return, both branches and both output writes. The real callee `0x004CFD66–0x004CFD70` calls `0x004CFD18–0x004CFD56`; that helper computes one plus the highest set-bit position, yielding zero for zero. The wrapper subtracts one, giving `floor(log2(size))` for nonzero size. Historical Ghidra export's missing argument and `unaff_r7` return expression are artifacts of inferred prototype/return-width: instructions show the consumed result is 32-bit r0. This pass does not edit that export.

For `size < 128`, unsigned comparison selects small bins and signed divide by 4 is equivalent to unsigned division because this branch limits size to 0–127. Output is `(fl=0, sl=size/4)`. Otherwise let `msb=floor(log2(size))`: output is `(fl=msb-6, sl=(size >> (msb-5)) XOR 32)`. ARM register LSR uses the low eight shift-count bits: `msb+251` becomes `msb-5` for this branch's msb 7–31. Stores write 32-bit values through original r1/r2 pointers; r4–r6 and stack are preserved.

Compare retained pinned upstream `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/tlsf/tlsf.c:512–529` and constants at 211–250. The exact two paths and constants match `mapping_insert`, providing behavioral evidence beyond a link-order label. This configuration inference concerns observed geometry; maximum allocator size and control layout require separate routines.

`validate.py` executes original function and both real helpers using Unicorn 2.1.4, allowing only their authenticated address spans. All 3,560 cases pass output and return ABI comparisons against the source-derived geometry: sizes 0–255, each bin boundary ±1 for msb 7–31, UINT32_MAX, and 1,000 seeded samples. No external provider is mocked. Emulation checks operational semantics, not hardware operation or full-domain formal proof. `validation.json` retains executed addresses and deterministic input hash.

REA pin `7aa4d768eb15317a63a476431ed75bafec086033` was checked. Its `src/domain/binaryTarget.ts` ELF admission would accept this authored ARM envelope, but admission cannot authenticate Thumb state or firmware load mapping. Its documented firmware lane does not add an independent execution/ISA oracle. No REA rerun or live Ghidra-MCP mutation was justified for this two-path routine after GNU listing and original-byte execution established its exact behavior.

## What changed and finite next boundary

Ablation accelerated call triage but supplied no new semantic fact beyond independently available instructions. The new retained inference is instruction-backed `mapping_insert` attribution and main-specific bin geometry, including correction of the historical callee prototype/return-width uncertainty. No new public dependency download is warranted because the existing pinned TLSF source already provides the comparator.

Next bounded question: authenticate and analyze `0x004CFF9A–0x004CFFC2` as the candidate `mapping_search`, then independently verify rounding overflow and its size precondition against its callers. Whole allocator maximum size, control layout, compiler identity and full P2 completeness remain open. This result is ready for independent review, not canonical acceptance. No classifier denial or model switch occurred.

Replay: `/Users/kalani/Repos/ablation/.venv/bin/python g2/analysis/shortcut-arm-tools-20261009-agent3/probe.py`, then the same interpreter with `validate.py` (Unicorn import comes from existing `/tmp/mspi-enable-python-deps`).
