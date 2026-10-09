# Clock-pump source attribution

The unresolved historical HF SetSource row at `0xA188` is the authentic public
`Cy_SysClk_ClkPumpSetSource`, exact over `[0xA188,0xA1C0)`:
44 instruction bytes and12 literal bytes, no relocations. This is one new
review-pending selected extent/56bytes. The historical symbol table is preserved.

The function validates the pump-clock source enum, updates the pump source
field while preserving other bits, and checks oscillator readiness before
reporting success. It does not select the HF source. This resolves the apparent
duplicate HF SetSource labels without merging or deleting census entries.
`verify.py` compares unchanged public object bytes; hashes and corrected mapping
are in `results.json`. Physical pump-clock switching remains untested.
