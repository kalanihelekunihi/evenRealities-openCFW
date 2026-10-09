The initial assertion selected1020714A for the PDM track byte load. Actual
fresh disassembly shows an AND at that address and the load at1020714E. The
assertion failed before producing results.json; the exact diagnostic was:
`('0x1020714a', ['1020714a: e4e72001 andi r7, r7, 1'], '0x21')`.
The address check was corrected to the actual byte-load instruction. Source
declarations, image bytes and decoded data were not changed to pass the check.
