# G2 bootloader SPOT-manager factory-trim loader source closure

Date: 2026-09-01

## Result

The 82-byte function at `[0x00429DA4,0x00429DF6)` is MIT production C in
`runtime_spotmgr_factory_trims_429da4.c`. Both reviewed compiler profiles emit
the exact stock body without relocations, SHA-256
`a69ea6c52f959eba65684feebd9651d2068cdd0d91caf8eb45d74e52969c61a4`.
The exact Apollo-main analogue is `0x005A3E24`, the direct caller is
`0x0042A042`, and five external shared literals are authenticated.

The portable model passes 50,000 indexed randomized INFO1 records. It loads
`trim_words[index + 1]`, assigns the four-bit CORELDO temperature trim, the
ten-bit active trim, and the seven-bit VDDC trim, then clears the readiness
byte exactly as stock does.

Physical INFO1 provenance, trim efficacy, voltage behavior, reset, and
cold-boot qualification are **blocked by unavailable physical evidence**.
No hardware operation or firmware-wide completeness claim occurred.
