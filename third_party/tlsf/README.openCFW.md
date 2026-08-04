# Matthew Conte TLSF v3.1 snapshot

This directory contains a byte-for-byte vendored snapshot of `tlsf.c` and
`tlsf.h` from the official
[`mattconte/tlsf`](https://github.com/mattconte/tlsf) repository. The snapshot
is integrated into the Apollo source overlay through
`components/apollo_main/core_overlay/runtime_tlsf.c` and its freestanding
`tlsf_compat/` headers. The upstream files remain byte-preserved inputs rather
than locally modified copies.

## Selected source candidate

- Selected snapshot:
  [`deff9ab509341f264addbd3c8ada533678591905`](https://github.com/mattconte/tlsf/commit/deff9ab509341f264addbd3c8ada533678591905)
- `tlsf.c` SHA-256:
  `2a0f8cfc9cfe6114ccdc6cf22339059440b16f1149b5107bead4ae4c3a0d50e2`
- `tlsf.h` SHA-256:
  `f7f73c48810ba60203095667c226e5a600a6ea0f69afba48efff6efbaa628d4f`

The exact source commit used by the G2 firmware cannot be proven from the
binary. The strongest defensible bound is the source-equivalent range from
[`a1f743ffac0305408b39e791e0ffb45f6d9bc777`](https://github.com/mattconte/tlsf/commit/a1f743ffac0305408b39e791e0ffb45f6d9bc777)
through the selected `deff9ab` candidate. The earlier endpoint contains the
large-allocation bounds fix observed in the firmware. The later commit changes
bitmap shifts from signed to unsigned integer literals, which is not
distinguishable in the reviewed target instructions for valid shift counts.

The firmware contains the IAR build path
`D:\01_workspace\s200_ap510b_iar_git\third_party\tlsf\tlsf.c`. Its retained
assertion line-number sequence matches this bounded source state with a
consistent one-line source offset.

## Recovered G2 configuration

The stock G2 build uses the 32-bit configuration:

- 4-byte pointers, `size_t`, and `ptrdiff_t`
- `TLSF_64BIT` unset and 4-byte allocation alignment
- `SL_INDEX_COUNT_LOG2 = 5`, giving 32 second-level lists
- `FL_INDEX_MAX = 30`, `FL_INDEX_SHIFT = 7`, and 24 first-level lists
- 128-byte small-block threshold
- 16-byte free-block header, 12-byte minimum block
- 4-byte allocation overhead and 8-byte pool overhead
- maximum block size `0x40000000`
- `control_t` size `0xC74`
- active assertions, `_DEBUG` disabled, and the generic `ffs`/`fls` path

TLSF is not thread-safe. The stock firmware provides locking in its surrounding
heap coordinators. The integrated source replacement preserves that boundary:
the generic and file-runtime coordinators still serialize their allocator
operations.

## Integrated source replacement

The overlay compiles the freestanding port prefix immediately before this
vendored source with the reviewed `thumbv7em-none-eabi` toolchain. All nine
externally reached stock TLSF entries are redirected in one atomic overlay
update:

- `tlsf_walk_pool` at `0x004D0580`
- `tlsf_block_size` at `0x004D05E4`
- `tlsf_pool_overhead` at `0x004D05FA`
- `tlsf_create_with_pool` at `0x004D06EC`
- `tlsf_get_pool` at `0x004D0716`
- `tlsf_malloc` at `0x004D0722`
- `tlsf_memalign` at `0x004D0744`
- `tlsf_free` at `0x004D0808`
- `tlsf_realloc` at `0x004D0868`

Together these redirects replace 710 stock bytes. The other 2,518 bytes in the
reviewed stock TLSF closure remain present and explicitly mapped as
compatibility bytes; they are not externally reached allocator entries.

The production compile is inspected as ARM ELF32 and pins the recovered G2
ILP32 constants. A separate import-free wasm32 module provides genuine
32-bit execution of pool creation/access, allocation, aligned allocation,
block-size queries, grow/shrink reallocation with data preservation,
free/coalescing, exhaustion, consistency checking, and 5,000 deterministic
randomized allocation/reallocation/free operations. The reviewed 9,018-byte
proof module has SHA-256
`198e6d5bae33d502605ac1696f764a4bd0cf1c7653433315c79afa862228c3eb`.
Native host tests remain useful for allocator semantics, but their 64-bit
process ABI is not treated as G2 ABI evidence.

## Stock binary evidence

For official G2 firmware `s200_v2.2.6.10`, the complete retained TLSF
code-and-literal closure is:

- address span: `0x004CFD18..0x004D09B3`, inclusive
- length: 3,228 bytes
- SHA-256:
  `007d8ac1f0e118281a07f6bde1049256800894d9684dff16e1d316f1ea4a7f9d`

The OTA payload at file offset `0x20` loads at `0x00438000`. Generated literal
islands occur inside the closure at `0x004D0604..0x004D0607`,
`0x004D06AC..0x004D06B3`, `0x004D06D6..0x004D06EB`,
`0x004D0802..0x004D0807`, `0x004D0852..0x004D0867`, and
`0x004D094A..0x004D09B3`.

Run the snapshot integrity and recovered-configuration check with:

```sh
python3 openCFW/third_party/tlsf/verify_snapshot.py
```

This verifies the upstream file hashes and license text, inspects the recovered
32-bit configuration without editing upstream files, and checks the stock span
when the pinned official firmware blob is present.

## License obligations

TLSF is distributed under the BSD 3-Clause license. The complete license text
is retained verbatim in `tlsf.h`. In summary:

- source redistributions must retain the copyright notice, conditions, and
  disclaimer;
- binary redistributions must reproduce them in documentation or other
  accompanying materials; and
- Matthew Conte's or contributors' names may not be used to endorse derived
  products without prior written permission.

Firmware distributions must reproduce the complete upstream notice in their
third-party license materials. This summary does not replace the verbatim
license in `tlsf.h`.
