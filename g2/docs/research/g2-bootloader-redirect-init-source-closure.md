# G2 bootloader `redirect_init` source closure

Status: production-integrated software closure; offline build and host semantics
validated; physical boot/stream validation blocked by unavailable authorized
responsive hardware

## Bounded stock contract

The authenticated G2 2.2.6.10 bootloader contains the complete
`product/s200/bootloader/config/redirect.c` `redirect_init` entry at
`[0x00415590,0x004155E8)`. The 88-byte body has SHA-256
`b53b1d0eae9d2787d431ae1950d956c54429fb339a67ee7f219ff7c01ffc0cd6`.
The recovered body:

1. calls retained CMSIS-RTOS2 `osMutexNew(NULL)` twice at `0x00416610`;
2. publishes the results to `0x2002712C` and `0x20027130`;
3. checks both handles only after both allocation attempts;
4. logs EasyLogger error level 1, line `0x271`, and returns `-1` if either
   handle is null; or
5. logs info level 3, line `0x275`, and returns zero after success.

The shared diagnostic identity is tag `redirect`, source path
`product\s200\bootloader\config\redirect.c`, and function `redirect_init`.
The exact messages are `Failed to create redirect mutex for IAR.` and
`redirect init with mutex protection.`. Both log paths terminate at the
retained `elog_output` entry `0x004176CE`.

The source boundary deliberately excludes the neighboring IAR `FILE`
wrappers. Their stream-object ABI and runtime behavior are not implied by this
closure and remain part of the bootloader software gap.

## Clean-room C and semantic tests

`components/bootloader/core_overlay/runtime_redirect_init.c` is the bounded
GPL-3.0-or-later clean-room implementation. Its source identity is 2,295 bytes
and SHA-256
`9df4daeea0af317c1556361a15f1625d5b1e9d00b3c72ae9b753de4608c3294f`.
The 1,982-byte ABI header hashes to
`d59de5e4176f72b95aa93c3e497de815bc29ac1ea816d2e3b8512d4349125414`.

The host fixture verifies successful publication, all three single/double
allocation-failure combinations, two calls even when the first allocation
fails, return values, log levels, source lines, source identity, and message
text. The target source compiles freestanding for Cortex-M55 with warnings as
errors.

## Production relocation closure

The canonical Apple clang 21 Cortex-M55 Thumb `-Oz` profile emits 132 text
bytes at overlay offset 664/runtime `0x00434710`. The relocated function has
SHA-256
`cbd1c5a521eef64ba9075a211311b71c8a025fd49fc4040814ba893c77260f22`.
Its authenticated 143-byte `.rodata.str1.1` closure hashes to
`617e0aef0ca7b9cc2d64b76394bd2203cf40de647d25e4caafe628433a0c30a0`;
the combined 275-byte closure hashes to
`ddb1d064bf765803fac4fc89c0b6c585f13b0ea7bcfc3b5ad7b78ee7d8e50922`.

All 12 relocations are strict. Four Thumb calls bind exactly to two
`osMutexNew` calls and two `elog_output` calls. Eight `R_ARM_REL32`
relocations bind only to the five authenticated strings inside the same
closure. No unreviewed undefined symbol or allocatable section is admitted;
the selected function's eight-byte `CANTUNWIND` metadata is authenticated and
deliberately discarded as non-executable metadata.

The complete stock entry is replaced by a non-linking Thumb `B.W` followed by
42 Thumb NOPs. The builder authenticates the entire 88-byte original span
before applying the patch and rejects any changed source, toolchain profile,
function layout, relocation, string section, destination, provider identity,
or ownership accounting.

The independent Homebrew clang 22.1.8 profile reproduces the same 132/143-byte
layout and 12-relocation graph. Its toolchain-specific complete overlay and
provider hashes are recorded in `overlay.json`; it is evidence of portable
compilation, not a byte-identity assertion across compiler releases.

## Current image accounting and safety boundary

After the adjacent C-runtime closures, the canonical complete bootloader
overlay is 1,338 bytes with SHA-256
`bd4d3fcb1c8fab3361e6d1a9dfdc5aff920d876589c8de37ecf7ac71dbf0f7ce`.
The raw provider is 149,938 bytes with SHA-256
`0e9b156ce6e251af4d15f7411ba09fcc509d9802281aeb4a5267f64f8e77f1a8`
and CRC-32C/MSB `0xEFD39833`. Provider accounting is 1,331 source-owned bytes,
1,800 generated patch-site bytes, eight generated alignment bytes, and 146,799
retained official bytes. It ends below Apollo main with `0x364E` bytes of
partition headroom.

`tools/analyze_g2_bootloader_redirect_init.py` rebuilds in an isolated local
directory and fails closed on every source, stock, relocation, patch,
ownership, manifest, and artifact pin. `make bootloader-redirect-init-closure`
runs that analyzer plus host semantics and the manifest consistency check.

The complete unsigned Apple package is 4,731,516 bytes with SHA-256
`95221a53071e8d5cec05ba5b3b58e291ceb5a9db4e0ba193be0b59a5d7e4190a`.
Its 4,322,480-byte flash plan hashes to
`a372e19791d80acaf92d1390e11367b09a560f3246ac4f792e8e33fcd9c0ba61`
and records 6,226 placed, two unresolved, five container-only, and six
protected regions. A complete Homebrew clang 22.1.8 profile refresh also
reduced all current Apollo-main C through the alternate compiler: its main
overlay/provider are 204,960/3,728,356 bytes with SHA-256
`5c857e687f2715965d159e07c723ae0a04838e063c2993c254761adbbe663429` and
`aee25953387faa833d06deabc059d72334af77027c089eba2f2af52aa57063c8`.
Together with the reviewed Linux boot provider it produces a 4,507,526-byte
package with SHA-256
`2db03bb1ae912db40231b9b19a33e9966f6d1695990b53777b0a9d72c0e754db`.
Both package profiles assemble byte-identically to their pins; neither is
signed or installed.

No command in this tranche signs, packages, installs, flashes, erases, resets,
or communicates with hardware. Physical acceptance requires an authorized,
responsive G2 right temple with boot UART and debugger visibility to validate
both mutex allocations, IAR stream serialization, failure diagnostics, and
continued boot. That physical evidence is unavailable, so the capability is
explicitly `implemented-in-source / hardware-validation-blocked`, not
hardware-complete.
