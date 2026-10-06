# TLSF upstream source and allocator match

Inspection date: 2026-10-06. This is a source attribution and host-behavior
artifact only. It does not claim compiled-code identity with the bootloader.

## Pin and source identity

- Repository: <https://github.com/mattconte/tlsf>
- Exact superproject gitlink (`git ls-tree HEAD third-party/upstream/tlsf`):
  `deff9ab509341f264addbd3c8ada533678591905`.
- Downloaded archive:
  <https://codeload.github.com/mattconte/tlsf/tar.gz/deff9ab509341f264addbd3c8ada533678591905>
- Archive SHA-256:
  `df67543d45ad5e67d96168b54022a0f4803f8d5ae9770d398e20dd9a0e2934d6`.
- `tlsf.h` identifies “version 3.1”; `README.md` history says 2016-04-10 v3.1.
  The same header contains the full 3-clause BSD notice; a separate copy is in
  `LICENSE.md`. The README states that the implementation is released under
  the BSD license. This confirms BSD-3-Clause source licensing for these files.
- The superproject's gitlink worktree remains uninitialized. The isolated
  source copy here contains upstream `tlsf.c`, `tlsf.h`, `README.md`, and the
  license extracted verbatim from the `tlsf.h` notice. SHA-256 identities are
  in `SHA256SUMS`.

## Target function and geometry comparison

The recovered bootloader allocator initializer at `0x0041FD70` has raw Ghidra
decompilation in `g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/`.
That export has not been independently reviewed, so the mapping is strong
structural attribution, not a completed source-to-object proof.

- `decomp/0041fd70.c` (`473e6095…147809`) clears `0x70800` bytes at the
  pointer stored at `DAT_0041FDA8`, then calls the two-stage initializer with
  that pointer and `0x70800`.
- In the target image, `DAT_0041FDA8` resolves to `0x20081000`. Thus the arena
  is `[0x20081000, 0x200F1800)`, total `0x70800` bytes.
- `decomp/00417240.c` (`b1bf9c45…407d72`) calls the control initializer, then
  the pool initializer with base `arena + 0xC74` and length `0x70800 - 0xC74`
  (`0x6FB8C`). This is the pool span passed by the bootloader wrapper; the
  actual free block is smaller after TLSF's pool/sentinel overhead and
  alignment.
- `decomp/0041711c.c` (`0afe4d24…1870bc`) initializes the control lists with
  24 first-level rows and 32 second-level columns. The pinned v3.1 source has
  `SL_INDEX_COUNT_LOG2 = 5`; in a 32-bit build it sets alignment log2 to 2
  and `FL_INDEX_MAX = 30`, yielding `SL_INDEX_COUNT = 32` and
  `FL_INDEX_COUNT = 30 - (5 + 2) + 1 = 24`.
- `layout_arm_assert.c` includes the pinned source and compile-time asserts
  the 32-bit Cortex-M55 control structure is exactly `0xC74` bytes and that
  both list dimensions are 24 × 32. It compiled successfully to ARM EABI5.
- The public v3.1 API exposes `tlsf_create`, `tlsf_add_pool`, `tlsf_malloc`,
  `tlsf_free`, and pool check/walk routines. The bootloader's recovered
  initializer follows the `create` + `add_pool` structure, with local wrapper
  functions and logging/error branches around control and pool construction.
  This is an unusually strong version/layout match and makes pinned v3.1 a
  practical source for the allocator core. It does not prove the wrapper bodies,
  allocation call sites, compile flags, runtime, or emitted bytes are identical.

The image's `0x70800` arena size, `0x20081000` base, `0xC74` control prefix,
and `0x6FB8C` pool argument come from the target image/raw export, not from a
simulator choice. Do not equate `0x6FB8C` with user-allocatable bytes.

## Compile and host fixtures

The pinned `tlsf.c` compiled together with `host_fixture.c` using Apple Clang
21.0.0 (`cc`, arm64 Darwin), `-std=c11 -O2`; the executable ran successfully.
The fixture exercises the bootloader-sized `0x70800` arena, 96/256/4096-byte
allocations, payload writes, zero/over-pool allocation failure, frees, heap
checks, and adjacent-block coalescing in a bounded 512-byte pool. Output:

```text
TLSF v3.1 characterization: SIZE_MAX returned block of 24 bytes
TLSF host fixtures passed: 96/256/4096, failure, adjacent coalescing
```

The `SIZE_MAX` case is deliberately characterization, not a passing failure
expectation: this revision's size-rounding overflow can turn a huge request
into a small allocation. Any caller that accepts untrusted lengths needs a
range check before calling the allocator. Whether the bootloader wrapper or
all call sites enforce such bounds is a separate binary audit.

The ARM layout assertion compiled with Apple Clang 21.0.0 for
`arm-none-eabi`, Cortex-M55, Thumb, EABI5, `-std=c99 -O2 -ffreestanding
-fno-builtin`. The Xcode MacOS SDK `usr/include` directory supplied C
declaration headers because no bare-metal sysroot is installed; there was no
link against Darwin libraries. Object output is ELF32 ARM EABI5. Host fixture
binary and layout object hashes are recorded below; both live in `/tmp`.

- Host fixture executable SHA-256:
  `ae7ea19dbadac8109d85ed041b072514a5e9183d24886068507a42e6bcee0ab3`.
- ARM layout assertion object SHA-256:
  `d4e91316c23c581364684b83e01a182645476c15a9e3bd08a6b3c0b495b45e3c`.

## Still unknown for the bootloader build

- Exact IAR EWARM/ILINK release, runtime libraries, optimization and ABI flags.
- How the source is wrapped/patched around public APIs and whether local
  compile-time overrides alter any internal values or error/reporting behavior.
- Exact source/config for logging, allocator locks, and every `malloc`/`free`
  call site; TLSF itself documents that it is not thread-safe.
- Whether any bootloader allocator calls can pass lengths near or above the
  block-size limit; the host characterization above establishes that unchecked
  `SIZE_MAX` is unsafe for this pinned code.
- Byte comparison of the full TLSF code/data region against an IAR build.
