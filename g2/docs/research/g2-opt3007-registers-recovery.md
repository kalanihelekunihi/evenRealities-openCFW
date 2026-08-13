# G2 OPT3007 register-map recovery

The retained `driver\sensor\als\opt3007\opt3007_registers.c` path is one
340-byte function plus a 20-byte pointer pool, for 360 physical bytes at
`[0x005135E0,0x00513748)`. Its exact retained diagnostic name is
`ti_opt3007_assignRegistermap`. Two direct entries, five calls, both adjacent
boundaries, the sole path reference, and the absence of stored, indirect, or
strict-interior entries are pinned by the analyzer.

The analyzer independently reconstructs all 57 output bytes from the stock
`movs`/`strb` sequence. They are 19 `(MSB, LSB, register)` triples covering
the result fields, every configuration field, low/high threshold exponent and
mantissa, manufacturer ID register `0x7E`, and device ID register `0x7F`.
This exactly follows Texas Instruments' official [OPT3007 SBOS864 register
map](https://www.ti.com/lit/ds/symlink/opt3007.pdf), initially published in
August 2017. The document is a functional specification, not a source-code
checkout, so there is no applicable repository commit.

Exact public searches for `ti_opt3007_assignRegistermap`, its diagnostic text,
and the retained filename found no source implementation. The code is therefore
classified as private G2 driver construction from a public TI specification,
not copied third-party source. Its only five calls are already admitted
EasyLogger diagnostics. The complete register schema is now available for a
clean-room replacement; production routing remains open.
