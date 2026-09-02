# G2 bootloader SPOT-manager factory-trim readiness source closure

Date: 2026-09-01

## Result

The guarded 20-byte wrapper at `[0x0042A036,0x0042A04A)` is MIT production C
in `runtime_spotmgr_factory_trims_ensure_42a036.c`. Apple clang 21.0.0 and
Homebrew clang 22.1.8 reproduce the stock body after one strict call
relocation at offset 12 to `0x00429DA4`. The linked SHA-256 is
`9c901638e2c0e882e9f92662df44aa585a49a2e160eb4f2a4c7b32b374ae7a06`;
the unrelocated SHA-256 is
`9d3ed2e40906fd9e19c9edc7a48294cd8aaa624d34951606b435f7d7bca3c68c`.
The stored Thumb entry pointer is at `0x0041D15C`, and the exact Apollo-main
analogue is `0x005A40B6`.

The portable form passes 100,000 randomized readiness states and calls the
loader only while factory trims remain pending.

Live INFO1 access, readiness transitions, trim efficacy, reset, and cold-boot
qualification are **blocked by unavailable physical evidence**. No hardware
operation or firmware-wide completeness claim occurred.
