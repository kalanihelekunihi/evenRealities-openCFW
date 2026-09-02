# G2 bootloader hardware channel and activation source closure

Date: 2026-09-01

The 126-byte channel encoder at `0x0042EAF6` and 64-byte activation service at
`0x0042ED60` are MIT production C. Both reviewed compilers and Apollo-main
analogues reproduce all 190 bytes exactly. Portable models cover handle,
channel-index and 32..63 range validation; every packed field; update counting;
idempotent activation; and control-bit state changes.

Live channel/control register effects are **blocked by unavailable physical
evidence**. No MMIO, flashing, reset, or completeness claim occurred.
