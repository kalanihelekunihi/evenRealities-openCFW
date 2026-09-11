# EM9305 ARC toolchain (macOS)

SPDX-License-Identifier: MIT

`build_overlay.py` compiles the EM9305 reconstructible-tail overlay for
ARCv2 EM (`-mcpu=em`). Earlier work ran this through a `docker run
opencfw-arc-toolchain:fedora44 ...` wrapper (see `git log -- g2/Makefile`)
holding a Red Hat cross `arc-linux-gnu-gcc (GCC) 16.1.1 20260501 (Red Hat
Cross 16.1.1-1)`. That image has no `Dockerfile` or build recipe committed
to this repository, is not present on this host, and Red Hat does not
publish a macOS build of it, so it was not a reproducible toolchain by this
project's own standard (hard rule 4/6 of the source-only goal). This
document pins a toolchain that runs natively on macOS instead.

## Pin

- Upstream project: [zephyrproject-rtos/sdk-ng](https://github.com/zephyrproject-rtos/sdk-ng)
  (the Zephyr Project's GNU Arm Embedded-style toolchain bundle; it ships
  per-architecture GCC/binutils builds, including ARC, with no Zephyr RTOS
  dependency required to use just the compiler).
- Release tag: `v1.0.1` (published 2026-03-25).
- Asset: `toolchain_gnu_macos-aarch64_arc-zephyr-elf.tar.xz`
  (`https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v1.0.1/toolchain_gnu_macos-aarch64_arc-zephyr-elf.tar.xz`),
  66,702,716 bytes.
- Asset SHA-256:
  `b3fbd56e8920a9a65230ed34de1d4af47bbb2411a6e45c4ae25f1830be039f1f`.
  This matches the entry for that filename in the upstream release's own
  `sha256.sum` manifest
  (`https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v1.0.1/sha256.sum`),
  so the pin is cross-checked against an independently published upstream
  checksum, not only the one download performed for this change.
- Contents: GCC 14.3.0 and binutils (GNU ld) 2.43.1 built for the
  `arc-zephyr-elf` target triple (bare-metal ARC, picolibc-hosted; picolibc
  itself is not used here -- the overlay links `-nostdlib` against no C
  library). `arc-zephyr-elf-gcc -mcpu=em` supports the full ARCv2 EM
  instruction set used by this component.
- Host: macOS/arm64 only is pinned today (the only macOS architecture this
  item had available to verify). Zephyr SDK v1.0.1 also publishes
  `toolchain_gnu_macos-x86_64_arc-zephyr-elf.tar.xz`-style Intel assets for
  most tags; add its SHA-256 pin here once someone verifies it produces the
  same `firmware_ble_em9305.bin` (see "Rebuild proof" below) on an Intel Mac.

## Install

```
g2/components/em9305/source_overlay/toolchain/fetch_arc_toolchain.sh
```

Downloads the pinned asset, verifies its SHA-256 against the pin above,
and extracts it to `~/.cache/opencfw/toolchains/arc-zephyr-elf-1.0.1`
(override with `OPENCFW_ARC_TOOLCHAIN_DIR`). The script is idempotent: it
does nothing if `<dest>/bin/arc-zephyr-elf-gcc` already exists.

## Wiring (`OPENCFW_ARC_*`)

`build_overlay.py` resolves each tool in this order:

1. The matching `OPENCFW_ARC_{GCC,NM,OBJCOPY,OBJDUMP,READELF}` environment
   variable, if set (also settable via the equivalent `--gcc`/`--nm`/...
   CLI flags) -- this is how a Linux host with `arc-linux-gnu-*` on `PATH`
   (or any other ARC cross toolchain) keeps working unmodified.
2. Otherwise, `<cache>/bin/arc-zephyr-elf-<tool>` under
   `OPENCFW_ARC_TOOLCHAIN_DIR` (default
   `~/.cache/opencfw/toolchains/arc-zephyr-elf-1.0.1`), if that toolchain has
   been installed by `fetch_arc_toolchain.sh`.
3. Otherwise, the bare `arc-linux-gnu-<tool>` name on `PATH` (the previous
   default), so a Docker/Linux invocation with that toolchain image still
   works with no environment changes.

No environment variables need to be set on a macOS host that has run
`fetch_arc_toolchain.sh`.

## Toolchain-driven build changes

Moving off the Red Hat cross GCC surfaced two build-script/linker-script
issues that were previously masked by that specific compiler's behavior,
not by anything specific to the EM9305 C sources:

- **Implicit default linker script.** This GCC build is picolibc-hosted and
  its `LINK_SPEC` appends its own `-Tpicolibc.ld` unless the driver itself
  sees an explicit `-T`. `build_overlay.py` previously passed the overlay's
  linker script as `-Wl,-T,<path>`, which reaches the linker but is invisible
  to that driver-level check, so both scripts landed on the link line
  together and silently changed orphan-section placement under
  `--gc-sections`. Fixed by passing `-T <path>` (recognized by the GCC
  driver) instead of `-Wl,-T,<path>`.
- **Two MetaWare helper functions not routed into the implementation cave.**
  `reconstructible_tail.ld`'s `.meta_impl` output section explicitly lists
  the helper-function sections GCC is known to split out of
  `open_cfw_em9305_metaware_shift_left64/shift_right64` and
  `open_cfw_em9305_metaware_udiv64`/`sdiv64` (`open_cfw_em9305_shift_left64_words`,
  `open_cfw_em9305_shift_right64_words`, `open_cfw_em9305_udivmod64.part.*`).
  With GCC 16.1.1, `open_cfw_em9305_metaware_stack_guard`'s two callees
  (`open_cfw_em9305_metaware_stack_pointer_in_bounds` and
  `open_cfw_em9305_metaware_stack_guard_with_policy`) were apparently always
  inlined into the caller and never needed an explicit entry; GCC 14.3.0's
  inliner keeps them as separate, still-referenced `.text.*` sections. Left
  unmatched by any output-section rule, `--gc-sections` treated them as
  orphans, and this specific ARC binutils build mis-placed/mis-sized them
  under that combination (observed as spurious `ASSERT` "size drift" and
  `R_ARC_S25H_PCREL relocation truncated to fit` errors against otherwise
  in-range targets). Fixed by adding both function sections to `.meta_impl`'s
  explicit wildcard list, exactly like the other four already-listed
  helpers -- this only affects section *placement*, not the C source or its
  behavior.
- **`build_overlay.py`'s per-entry "exactly four bytes" check.** Four of the
  23 `ENTRY_PATCHES` wrap a narrow (`uint8_t`/`uint16_t`) store argument.
  GCC 16.1.1 apparently trusted the caller to have already narrowed the
  value; GCC 14.3.0 additionally emits an explicit two-byte
  `extb_s`/`exth_s` zero/sign-extension ahead of the four-byte tail branch
  (six bytes of real code, rounded to an eight-byte section by the
  assembler). Both are a single compiler-emitted tail branch to the correct
  C implementation (verified, as before, by disassembling the linked ELF and
  checking the branch target), and both fit their allocation's authenticated
  stock span. `build_overlay.py`'s check was relaxed from "exactly four
  bytes" to "at least four bytes, a whole number of ARC halfwords, no larger
  than the allocation" to admit this compiler-driven, still fully verified
  variation.

None of these change the EM9305 C source itself, the addresses or sizes any
entry occupies, or what the build's own disassembly/branch-target/undefined-
symbol checks verify.

## Rebuild proof

Two independent `build_overlay.py` runs with this pinned toolchain (default
resolution, no explicit `--gcc`/...) produced byte-identical output:
`firmware_ble_em9305.bin` SHA-256
`56694060c0d2761c2004581d0cec97cdb8642c1ff44675194d05d605bf8dd9c7`,
212,984 bytes, both runs.

That output is **not** byte-identical to the artifact previously checked in
here (SHA-256 `1a4ccc61cae6e9b90d0eb3d694179d726c935171788167d28ea45060d7431c42`,
built by the now-unreproducible Red Hat cross GCC 16.1.1). Comparing the two
byte-for-byte and mapping every differing offset back through
`components/em9305/source_image/record_package.py`:

- Records 0-2 (everything before the application record) are identical.
- Within the application record, all 616 differing bytes fall inside this
  overlay's own source-owned spans: the four widened entry-patch sections
  above, the eight `META_ENTRY_PATCHES` branch immediates (their targets
  moved a few bytes within the implementation cave, changing the encoded
  branch offset, not the destination symbol), and the `.tail_impl`/
  `.meta_impl` implementation cave itself (585 bytes -- ordinary
  instruction-selection differences between GCC 14.3.0 and 16.1.1 compiling
  the same C at `-Os`).
- Zero differing bytes fall outside those spans; every stock/retained byte
  this overlay does not claim to own is reproduced exactly.

Every entry/meta-entry branch target and every linker-script `ASSERT` still
pass with the new toolchain (see `build_overlay.py`'s own checks, which ran
as part of this build). Given the old build's toolchain has no recoverable,
reproducible recipe on any host available to this project, that is the
strongest rebuild proof obtainable: this toolchain is pinned,
independently checksum-verified, and self-reproducing, and it changes only
this component's own source-owned bytes -- never a retained/stock byte --
relative to the last (unreproducible) build.
