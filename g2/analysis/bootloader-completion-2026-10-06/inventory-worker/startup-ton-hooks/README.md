# Startup tone trim hooks

This isolated source candidate reconstructs the stock routines at
`0x42f41a..0x42f4b2` and `0x42f4b2..0x42f5f0` from the locked G2 2.2.6.10
bootloader. It is an analysis artifact, not part of an active firmware build.

The first routine has no callees. The second routine retains two explicit
external cuts: `0x41c838(uint32_t)` and `0x41d1c0(uint32_t)`. Its flash table
at `0x433f20` remains an authenticated read from the same locked image.

`make test` compiles the source independently to Thumb ELF and compares stock
and source behavior under Unicorn with deterministic memory-mapped register
fixtures. The tests compare return values, writes, and cut-call arguments,
while checking executed stock instructions remain within the stated extents.
This does not establish physical MMIO semantics, whole-program callers, or
source identity with any HAL release.

The Apollo510 HAL 5.1 replay documents declarations for the TON configuration
API (`am_hal_spotmgr.h`) and related settings, but does not provide the bodies
of these stock callbacks. The source below is therefore a behavioral
reconstruction of the locked bytes, not copied or license-inferred HAL source.
