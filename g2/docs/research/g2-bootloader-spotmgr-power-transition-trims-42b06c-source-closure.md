# G2 bootloader SPOT-manager power-transition trim transaction source closure

Date: 2026-09-01

## Result

The 552-byte function at `[0x0042B06C,0x0042B294)` is BSD-3-Clause
production C in `runtime_spotmgr_power_transition_trims_42b06c.c`. Both
reviewed compilers reproduce the exact stock body after strict call
relocations at offsets `0x76` and `0x90` to delay provider `0x0041D1C0`.
Linked SHA-256 is
`44271365df4592f33c91286690e4e75e328a8dd11127aa934bec2c571292c377`;
unrelocated SHA-256 is
`35646af379886e8764cde56a2bf9bc6fb22e94f53ea178c5c60dd1727d190127`.

Direct callers are `0x0042B2DA`, `0x0042B348`, and `0x0042B65C`. The
Apollo-main analogue at `0x005A0D9C` shares 540 of 552 bytes in four
address-coupled runs. The transaction temporarily and saturatingly biases
the 10-bit core and 6-bit flash trims, applies two 20-cycle delays around the
transition gate, selects authenticated five-bit trims for power states 0–7,
applies transition-specific overrides, updates three SIMOBUCK fields, clears
the gate, and restores both temporary biases. A deterministic host test
covers 10 power states, 21 transition selectors, and 50 randomized register
sets per route.

Physical voltage transitions, delay calibration, rail stability, reset, and
cold-boot qualification are **blocked by unavailable physical evidence**. No
hardware operation or firmware-wide completeness claim occurred.
