# G2 bootloader MSPI command-queue init boundary

The complete 44-byte body at `[0x00423F28,0x00423F54)` is the AmbiqSuite
5.1.0 static helper `mspi_cq_init`. Its stock SHA-256 is
`8e2e5409620c3c1b334d8c3ede2ea19b20a31471e40a0c8b0c88f6550a7e9b05`,
and its sole direct caller is `0x0042509C`. The exact source fragment is in the
authenticated `am_hal_mspi.c` from upstream commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b` under BSD-3-Clause.

## Exact adapter ABI

The register arguments are MSPI module, command-queue length, and transfer
control buffer. The adapter constructs a twelve-byte `am_hal_cmdq_cfg_t` on
the stack: entry count is `length / 2`, the buffer is the third argument, and
priority is `AM_HAL_CMDQ_PRIO_HI` (`1`). It calls `am_hal_cmdq_init` with
hardware interface `AM_HAL_CMDQ_IF_MSPI0 + module`, configuration pointer, and
the address of the MSPI state's command-queue handle.

Stock code exposes the exact IAR ABI detail that the interface enum is narrowed
to one byte before the call. It performs no module validation of its own. The
state address uses the full 32-bit module, base `0x2001CAA0`, stride `0x8D0`,
and handle offset `0x828`. The far literal at `0x00424AEC` is exactly the state
base. The MIT software-only model preserves the one-byte conversion, 32-bit
address arithmetic, absence of wrapper-side validation, config layout, and
provider return value without dereferencing SRAM or MMIO.

## Provider and license closure

The call at `0x00423F4E` reaches `[0x00427794,0x00427878)`, exactly the
AmbiqSuite `am_hal_cmdq_init` semantics. The provider validates one of twelve
IOM/MSPI interfaces, a non-null config/buffer/handle output, at least two
entries, and an uninitialized state. It initializes `gAmHalCmdq`, its hardware
register-table pointer and command-queue registers, then returns the state
handle. The same body is independently called by the IOM path at `0x0042C40E`.

The provider's retained literals close at `0x200262F0` (`gAmHalCmdq`) and
`0x00430880` (`gAmHalCmdQReg`). The latter is a 480-byte table: twelve
40-byte entries for IOM0 through IOM7 and MSPI0 through MSPI3. Its stock
SHA-256 is
`1ed1fa3682f9c16c403ee0e6cee7761b70ca610656a2b6e56de3f0b05cee7fea`.
The isolated evidence fragment pins upstream `am_hal_cmdq.c` Git blob
`0a286e565cad27cef801c389b5dedae826a2669a`; it retains the complete Ambiq
BSD-3-Clause notice and is intentionally not compiled.

All attributable source in this graph is BSD-3-Clause. Source and source-built
binary redistribution are available under those terms. Redistribution
authority for corresponding bytes extracted from Even's official package is
not inferred and remains unresolved.

## Fail-closed toolchain result

With default enum width, both reviewed Clangs emit 40 bytes with SHA-256
`eab31502d7ca042cdbb3c646be9426b8ce2108b0381a7a2bdaa872e8257012ae`.
With `-fshort-enums`, both emit 44 bytes with SHA-256
`747f4344fbd039cf5f0fa93e55c3748000925237f7410304164b2eb3c491c413`.
The latter closes the stock one-byte enum ABI and body size, but not instruction
selection, prologue, state-literal relocation, or literal-pool placement. It
does not equal the stock hash.

No exact unmodified-upstream compiler candidate is admitted without the stock
IAR release, short-enum setting, remaining code-generation options, and
literal-pool rules. The typed boundary therefore continues to return
`OPEN_CFW_BOOT_MSPI_CQ_INIT_EXACT_TOOLCHAIN_UNRESOLVED` for that route.

Subsequent concurrent work admitted a MIT clean-room target
implementation whose 44 linked bytes exactly match stock and whose sole
relocation at offset `0x26` reaches the typed retained `am_hal_cmdq_init`
provider at `0x00427794`. The host implementation is the same software-only
model exercised by this audit. This distinct production route moves the
source-owned frontier through CQ termination, control, and pause to
`0x0042403E`; hardware validation is blocked by unavailable physical evidence.

The successor `[0x00423F54,0x00423F8E)` is the 58-byte AmbiqSuite
`mspi_cq_term` body. A subsequent independent admission closed its exact
source identity and provider edge to `am_hal_cmdq_term` at `0x00427AD6`, and
the following enable/disable pair through `0x00423FB8`. See
`g2-bootloader-mspi-cq-term-423f54-423f8e-source-closure.md` and
`g2-bootloader-mspi-cq-control-423f8e-423fb8-source-closure.md`. No hardware,
MMIO, flashing, or signing operation was performed.
