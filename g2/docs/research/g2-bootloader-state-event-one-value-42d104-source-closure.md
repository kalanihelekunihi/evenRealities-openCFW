# G2 bootloader state-one register-tuning source closure

The authenticated interval `[0x0042D104,0x0042D3BC)` is production-routed
from `runtime_state_event_one_value_42d104.c`. Apple clang 21 and Homebrew clang
22 reproduce all 696 stock bytes after three strict delay-provider relocations.
The stock body SHA-256 is
`cf108ad5215cbb620832a3e19e1eede59c9a5726494715ae311b14c0ffa07994`;
the unrelocated body SHA-256 is
`1a14892f813bdf7509d0f4df3813866b5a77ab47ab377d72e592ed6cf4647480`.
Its sole caller is `0x0042D5A6`; no interior or stored-pointer ingress exists.
The Apollo-main analogue at `0x005A0328` matches 684 of 696 bytes, with all
three four-byte differences confined to image-local delay calls. Sixteen
literal cells pin the retained-state and MMIO addresses.

The service saves the inactive state fields and applies a saturated low-six
increment with a 15-microsecond delay, or performs the active sequence: save
and select the four-bit mode, apply a bounded ten-bit delta, select the
temporary low-six value, run ordered 5/10-microsecond delays around the power
mask, optionally saturate two seven-bit trim fields, publish four paired
tuning fields according to the input profile, clear power, restore the delta,
and choose the final low-six state. Portable tests cover inactive save and
saturation, adjusted profile variants and saturation, default profile routing,
delay accounting, power cleanup, and field preservation.

The 8,839-byte MIT source has SHA-256
`43a5e400d060abd063b18ce00fac00a0c27f9c1d18a355973d8aa52e0ab4c7c8`.
Focused tests, strict dual-toolchain compilation, manifest ownership, provider
conservation, and unsigned complete-image assembly are verified offline. Live
MMIO semantics, clock/power stability, delay accuracy, trim effects,
peripheral response, interrupt races, reset, and cold boot are blocked by
unavailable physical evidence. No signing, flashing, reset, or hardware access
occurred; functional completeness is not claimed.
