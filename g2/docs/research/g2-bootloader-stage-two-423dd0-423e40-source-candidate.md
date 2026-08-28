# G2 bootloader stage-two frontier source candidate

The sequential frontier beginning at `0x00423DD0` contains two complete
adjacent functions and one literal island through `0x00423E40`. The tranche
is 112 bytes: 104 executable bytes and eight bytes of authenticated SRAM
address constants. After its two typed call relocations are applied, the
maintained MIT mnemonic assembly reproduces the complete stock range under
both reviewed Cortex-M55 Clang profiles. The normalized range hashes to
`b6f037077c2577f042a56ca31101ce7c6734eda572bf1d613195bb3967064c12`.

## Stage-two status seam

The 60-byte function at `0x00423DD0` has one direct caller, guarded teardown
at `0x0041FAAE`. It enters the retained critical-section primitive at
`0x0041B8EC`, decrements the byte at `0x200271C3` when nonzero, and returns
status three while that counter remains nonzero. At zero it clears the byte at
`0x200271C2`, calls the already source-owned debug-disable function at
`0x00422468`, normalizes debug status three to zero, restores the saved
`PRIMASK`, and returns. The adjacent literal words are exactly `0x200271C2`
and `0x200271C3`.

The MIT target assembly is an exact independent clean-room candidate. During
this wave, an equivalent exact source admission was added concurrently at the
same runtime address as
`open_cfw_bootloader_hw_control_critical_423dd0`. The current overlay pins that
MIT clean-room C body to the same 60-byte stock hash and the same
two relocation targets. This analyzer explicitly verifies that concurrent
ownership instead of incorrectly continuing to call the address opaque.

That production source admission does not erase the provider redistribution
boundary. Debug-disable is already represented by exact BSD-3-Clause-
compatible source in the current overlay. Critical-save is an eight-byte
first-party Cortex-M primitive whose observed ABI and behavior are fully
typed, but attributable maintained source and binary redistribution authority
have not been established. Its official bytes are neither copied into this
MIT candidate nor relicensed. A standalone redistributed binary still remains
fail-closed on that retained provider even though the calling function is now
source-owned.

## Provider-free mode-flags leaf

The 44-byte function at `0x00423E14` has direct callers at `0x00425E60` and
`0x00425FFE`. It reads a mode word at context offset `0x838`. Mode one adds
flags `0x40A0` and advances the mode to two; mode two replaces the flags with
`0x4000`; all other values add `0x4080`. It has no calls, literals, runtime
providers, or hidden ABI edges. Its exact MIT source was production-admissible
in this isolated wave. An equivalent exact MIT clean-room C body
has since landed concurrently as
`open_cfw_bootloader_hw_control_state_423e14`; the analyzer now pins that
production ownership and the shared overlay/package changes remain external
to this isolated audit.

The assembly places the two functions in independent sections so the
provider-free leaf can later be admitted without importing the status seam's
critical-save blocker. The host model covers every counter transition, debug
status normalization and propagation, mask restoration, guard effects, and
all three mode branches.

## Remaining frontier

The next sequential body is `[0x00423E40,0x00423E8A)`. The subsequent Wave 4
audit identifies it as AmbiqSuite 5.1.0 `mspi_fifo_write`, identifies retained
service `0x0041D246` as `am_hal_delay_us_status_check`, and proves the far
literal at `0x0042499C` is `MSPI0_BASE`. BSD source availability is closed,
but exact IAR emitted-body identity and official-byte redistribution remain
unresolved, so the separate
`g2-bootloader-mspi-fifo-write-423e40-423e8a-boundary.md` stays fail-closed.
No production overlay, global package manifest, hardware, signer, transport,
flashing, or publication path was changed.
