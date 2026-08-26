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
EasyLogger diagnostics.

`components/apollo_main/core_overlay/opt3007_registers.c` now provides the
clean-room production implementation. The target build deliberately disables
loop and SLP vectorization for this leaf so the reviewed Cortex-M55 output is a
scalar, four-byte-aligned, 224-byte function with zero relocations. It writes
the exact 57 authenticated descriptor bytes and safely returns for a null
destination. A guarded `B.W` redirect replaces the complete 340-byte stock
body while the 20-byte authenticated diagnostic/alignment pool remains
official.

The canonical overlay/component/package identities after this increment are
239,904 / 3,763,300 / 4,541,794 bytes with SHA-256 values
`2def566dbf70594c89471066a7cd17f6d1fa94196f65ff48237385396e9cfd19`,
`7228edb650fe39bda63480691fe94ed59d0807ca5e30846d35ec08e134e08350`,
and `c146ea7977a5521aa1df24a1a285768d7e2396fab96f117315a5baa2dcb65998`.
The 2,562,590-byte flash plan has 3,676 placed, two unresolved, five
container-only, and six protected regions. Host byte-oracle and strict target
compile tests pass. Live OPT3007 bus behavior remains hardware-blocked because
no authorized responsive G2 pair is physically available; no image was signed
or flashed.
