# G2 bootloader retained hardware-event apply source closure

The authenticated Thumb entry `[0x0042C0B2,0x0042C222)` is a 368-byte event
acknowledgement, drain, timed register-pulse, and terminal restoration service.
Its direct callers are `0x0042C7D0` and `0x0042C92A`; no interior or stored
entry exists. The Apollo-main analogue at `0x0055BDAC` shares 361 of 368 bytes.

`runtime_hw_event_apply_42c0b2.c` is first-party MIT clean-room source. Apple
clang 21 and Homebrew clang 22 reproduce the stock body exactly after the
single strict delay-provider call at offset `0xC8`. Relocated SHA-256 is
`a3d5075b7f480a21b071c587bb343466ca39d411ed426927e82b22168591937e`;
unrelocated SHA-256 is
`d6834d461bd966d94e411a233499545d78421cec37e7901ba6e084eb4bbede2d`.
Portable tests cover terminal register restoration, drain count and command
publication, ready and non-ready pulse paths, saved-register restoration, and
delay scaling. The base-register and drain-command literals at `0x0042C6E8`
are pinned.

No hardware operation occurred. Live retained-SRAM, MMIO, clock, peripheral
timing, concurrency, interrupt, reset, and cold-boot qualification is blocked
by unavailable physical evidence. Firmware-wide completeness is not claimed.
