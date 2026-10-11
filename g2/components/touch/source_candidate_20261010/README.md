# Touch source candidate (2026-10-10)

Run `python3 build.py` from any directory. The script compiles the 45 existing
offline C translation units plus pinned SCB I2C/common source and the verified
reset-data definitions for Cortex-M0+. It rebuilds MSCLP, SysLib and libgcc
providers from pinned source, flags, headers, compiler and container image on
each run; each object must match its previous source-build hash. It packages the relocatables in
`build/touch-source-candidate.a`. `build/receipt.json` records compiler flags,
source and transitive include hashes, object hashes, and compile diagnostics.
`build/symbols.txt` records the global/weak archive symbol census. The build consumes
no original executable body and creates no firmware image.

This archive is an integration candidate for bounded offline modules, not a
whole touch source build. See the round-two report under `g2/analysis/`.
