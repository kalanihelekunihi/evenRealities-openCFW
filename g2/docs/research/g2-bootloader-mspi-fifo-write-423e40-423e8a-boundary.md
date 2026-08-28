# G2 bootloader MSPI FIFO-write frontier boundary

The complete 74-byte body at `[0x00423E40,0x00423E8A)` is the AmbiqSuite
5.1.0 static helper `mspi_fifo_write`. Its stock SHA-256 is
`8ea56d5bbd1d671d999791ea24b747f4083048a9bfe169360470ebf4d36914d1`,
and its sole aligned direct caller is `0x0042640C`. The identity is closed
against the authenticated unmodified `am_hal_mspi.c` from upstream commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b` under BSD-3-Clause.

## Exact ABI and far literal

The four register arguments are MSPI module, word pointer, byte count, and
timeout. Modules zero through three are accepted; larger values return
`AM_HAL_STATUS_OUT_OF_RANGE` (`5`). For each word whose byte offset is below
the requested byte count, the helper writes `MSPIn(module)->TXFIFO` and calls
`am_hal_delay_us_status_check` for `TXENTRIES != 16`. The helper does not stop
on an intermediate timeout and returns the final status; a zero byte count
returns success.

The apparent far dependency at `0x0042499C` is not executable code or private
state. It is the word `0x40060000`, exactly `MSPI0_BASE` in the authenticated
Apollo510 CMSIS header. The source and stock body agree on the `0x1000` module
stride, `TXFIFO` offset `0x10`, `TXENTRIES` offset `0x18`, mask `0x3F`, full
value `0x10`, and four-module bound.

## Bounded provider graph

The call at `0x00423E7A` targets the 68-byte
`am_hal_delay_us_status_check` body at `0x0041D246`. Its exact source is the
AmbiqSuite 5.1.0 `am_hal_utils.c` object at upstream Git blob
`13372860cfd972b02fba13be767d0015b5b58436`, size 12,173 and SHA-256
`20a26a34ceb7835fa2a233bbbf2454f5f43e13aeb1ab43d51f5ff14a38f579a3`.
That provider calls `am_hal_delay_us` at `0x0041D1C0` with duration one; the
delay body terminates at the documented Apollo510 boot-ROM cycle seam
`0x00000040`. All three source identities and ABIs are attributable to the
same BSD-3-Clause AmbiqSuite revision.

Source redistribution and source-built binary redistribution are permitted
subject to the BSD conditions. That does not establish permission to
redistribute the corresponding bytes extracted from Even's official package,
which remain excluded from a community distribution.

## Fail-closed admission decision

Exact upstream source identity is not the same as exact emitted-body identity.
The stock image carries IAR runtime/compiler signatures, but the precise IAR
release and compiler options for this static helper remain unavailable. Both
reviewed Cortex-M55 Clang profiles compile the unmodified helper identically
when preserving the otherwise-inlined function, but emit an 80-byte body with
SHA-256 `f7a88e1c056f8fc82c62783cf6e29266093356d73615bb4ef391b4fd50e1a796`,
not the 74-byte stock body.

No exact unmodified-upstream compiler candidate is therefore asserted. The MIT
boundary and software-only semantic model under
`research/admission/bootloader_mspi_fifo_write_423e40/` preserve the complete
typed contract while returning
`OPEN_CFW_BOOT_MSPI_FIFO_WRITE_EXACT_TOOLCHAIN_UNRESOLVED`. Subsequent
concurrent work admitted a MIT clean-room target implementation
that emits the exact 74 stock bytes with a single typed relocation to the
retained status-check provider. That distinct production route is documented
in `g2-bootloader-mspi-fifo-write-423e40-423e8a-source-closure.md`. Subsequent
source admission of the FIFO-read and CQ-init successors moved the current
official opaque region through CQ termination, control, and pause to
`0x0042403E`.

The next sequential complete body is `[0x00423E8A,0x00423F28)`. Wave 5 closes
it as exact AmbiqSuite 5.1.0 `mspi_fifo_read` source and ABI, but keeps it
fail-closed because Apple and Homebrew Clang emit different sizes and neither
matches the stock IAR body. See
`g2-bootloader-mspi-fifo-read-423e8a-423f28-boundary.md`. No hardware, MMIO,
flashing, signing, package, or global production operation was performed.
