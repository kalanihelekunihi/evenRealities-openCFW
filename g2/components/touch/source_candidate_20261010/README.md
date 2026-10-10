# Touch source candidate (2026-10-10)

Run `python3 build.py` from any directory. The script compiles the 45 existing
offline C translation units for Cortex-M0+ and packages relocatable objects in
`build/touch-source-candidate.a`. `build/receipt.json` records compiler flags,
source and transitive include hashes, object hashes, and compile diagnostics.
`build/symbols.txt` records the raw archive symbol census. The build consumes
no original executable body and creates no firmware image.

This archive is an integration candidate for bounded offline modules, not a
whole touch source build. See the round-two report under `g2/analysis/`.
