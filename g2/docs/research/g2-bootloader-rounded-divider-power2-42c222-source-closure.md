# G2 bootloader rounded-divider and power-of-two helper source closure

Date: 2026-09-01

## Result

The helpers at `[0x0042C222,0x0042C256)` (52 bytes) and
`[0x0042C256,0x0042C26A)` (20 bytes) are MIT production C in
`runtime_rounded_divider_power2_42c222.c`. Both reviewed compilers reproduce
the exact bodies without relocations. Their SHA-256 values are respectively
`84a7909276921edf87861325fa09f547e536659109a2de4eeb1fd171f7f57411` and
`c7c013df5ce01fcc66215af1337fed966a975393591a7bc7e17ebcf71bde8213`.
Apollo-main bodies at `0x0055BF1C` and `0x0055BF50` are byte-for-byte exact.

The first helper builds an odd-factor divider, performs unsigned division,
and rounds upward only when the remainder is strictly greater than half the
denominator. The second recognizes nonzero powers of two. Direct callers are
authenticated at `0x0042C394`, `0x0042C3C8`, and `0x0042C3B2`. Host tests
cover 100,000 valid randomized divider tuples and more than 100,000 power-of-
two inputs.

Any hardware clock-divider use and resulting peripheral timing are **blocked
by unavailable physical evidence**. No hardware operation or firmware-wide
completeness claim occurred.
