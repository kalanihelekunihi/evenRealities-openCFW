# G2 bootloader MSPI FIFO-read frontier boundary

The complete 158-byte body at `[0x00423E8A,0x00423F28)` is the AmbiqSuite
5.1.0 static helper `mspi_fifo_read`. Its stock SHA-256 is
`9bb93dd67b7844ce1e9d75d6a165667cc38f27b45ad937ea7815c357d8ce4a7b`,
and its sole aligned direct caller is `0x004263F6`. The identity is closed
against the authenticated unmodified `am_hal_mspi.c` from upstream commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b` under BSD-3-Clause.

## Exact ABI and data behavior

The four register arguments are MSPI module, destination pointer, byte count,
and timeout. Modules zero through three are accepted; larger values return
status five. The helper splits the byte count into complete 32-bit words and
zero through three leftover bytes. Before every FIFO read it calls
`am_hal_delay_us_status_check` for `RXENTRIES != 0`; any nonzero provider
status returns immediately without reading that word. Complete words are
stored directly. A final partial word is copied least-significant byte first
without overwriting bytes beyond the requested length.

The two far loads resolve to the same word at `0x0042499C`, which is exactly
the authenticated Apollo510 CMSIS `MSPI0_BASE` value `0x40060000`. The stock
body and source agree on the `0x1000` module stride, `RXFIFO` offset `0x14`,
`RXENTRIES` offset `0x1C`, mask `0x3F`, target value zero, and not-equal mode.

## Provider, license, and redistribution closure

Both calls target the 68-byte `am_hal_delay_us_status_check` body at
`0x0041D246`. It calls the 92-byte `am_hal_delay_us` body at `0x0041D1C0`,
which terminates the bounded graph at the documented boot-ROM delay-cycle ABI
at `0x00000040`. The provider source is AmbiqSuite 5.1.0 `am_hal_utils.c`,
upstream Git blob `13372860cfd972b02fba13be767d0015b5b58436`, size 12,173,
SHA-256 `20a26a34ceb7835fa2a233bbbf2454f5f43e13aeb1ab43d51f5ff14a38f579a3`.

All source in this graph is available under BSD-3-Clause, permitting source
and source-built binary redistribution under its conditions. Permission to
redistribute the corresponding bytes extracted from Even's official package
is not inferred and remains unresolved.

## Fail-closed toolchain decision

The upstream source identity and ABI are exact, but the emitted body cannot be
claimed exact without the stock IAR compiler release and options. With
`-Oz -fno-inline`, Apple Clang emits 156 bytes with SHA-256
`e229e94145fb9563f438954cd0f35394cf5fa0563576c62e8d86958c5e7123c9`,
while Homebrew Clang emits 148 bytes with SHA-256
`c3ab2557e0dfc8cafc6c215072fad483b0b7c67f6a27e98e5ed7b85e186bf97a`.
Neither matches the 158-byte stock body, and the two reviewed profiles do not
match one another.

No exact unmodified-upstream compiler candidate is admitted. The MIT typed
boundary and software-only model under
`research/admission/bootloader_mspi_fifo_read_423e8a/` preserve both timeout
paths, full-word reads, partial-copy behavior, module validation, MMIO address
derivation, and provider arguments while returning
`OPEN_CFW_BOOT_MSPI_FIFO_READ_EXACT_TOOLCHAIN_UNRESOLVED`. Subsequent concurrent
work admitted a MIT clean-room target implementation that emits
the exact 158 stock bytes with two typed relocations to the retained
status-check provider. That distinct route is documented in
`g2-bootloader-mspi-fifo-read-423e8a-423f28-source-closure.md`. Subsequent
source admission of CQ init, termination, control, and pause moves the current
production opaque region to `0x0042403E`.

The next complete sequential body is `[0x00423F28,0x00423F54)`. Wave 6 closes
it as the exact AmbiqSuite 5.1.0 `mspi_cq_init` source identity and closes its
`am_hal_cmdq_init` provider, short-enum ABI, and state/register literals, while
retaining a fail-closed exact-toolchain boundary. See
`g2-bootloader-mspi-cq-init-423f28-423f54-boundary.md`. No hardware, MMIO,
flashing, signing, package, or global production operation was performed.
