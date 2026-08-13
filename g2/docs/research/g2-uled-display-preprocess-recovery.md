# G2 ULED display preprocessing recovery

Status: complete linked-object census and host/Thumb-qualified clean-room
candidate; not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path `driver\uled\display_preprocess.c` owns the
linked `buffer_sync_to_fb` body at `[0x0046C73C,0x0046C984)`: 584 bytes,
SHA-256
`129ff88839a933f90af5ae9f3417a3ff53f90314dde5b80a5446a7147e6c3869`.
Its IAR-emitted literal/template pool is discontiguous at
`[0x0046CA74,0x0046CAB4)`: 64 bytes, SHA-256
`9f5750f76e457c7d475b1403522a3a45ba0a020fedf1aa6e4d55a74de814afc0`.
The two owned segments total 648 bytes with concatenated SHA-256
`29ec9f01a08de4de1205cb2b1e97aeeb0de99d0847452b3de9419e07c84d2aa3`.

One direct call at `0x0046CA64` roots the body. The function has 23 genuine
direct provider calls. A raw Thumb-immediate sweep additionally resembles a
call at `0x0046C972`, but that address is the second halfword of the valid
32-bit `sdiv` at `[0x0046C970,0x0046C974)` and is excluded. No stored entry
pointer, `B.W`, direct branch, or aligned raw word targets the body or a strict
interior. The only two raw interior-looking words begin at odd byte offsets
`0x0048FEA9` and `0x004B34E9` and are instruction-byte overlaps.

## Contract

The eight arguments are destination pointer, source pointer, destination
width/height, source width/height, and X/Y offsets. The stock function asserts:

- both pointers are non-null and eight-byte aligned;
- destination width and height strictly exceed source width and height;
- X offset, source width, and destination width are even.

The function copies the authenticated 28-byte template beginning with control
word `0x00000619`, then fills a destination descriptor:

| Field | Stock value |
|---|---|
| packed dimensions | `(destination_height << 16) | destination_width/2` |
| stride | `destination_width/2` |
| pixel count | `destination_width * destination_height / 2` |
| destination and alias | destination pointer |

The zero-initialized 16-byte source region stores
`destination_width/2 - 1` and `destination_height - 1` in its final two words.
GPU start is called with flags zero. A result other than byte value one is
diagnosed and returns. Success configures/enables destination channel zero,
configures the source with width/stride `source_width/2`, source height,
format nine and flags zero, applies offset `(offset_x/2, offset_y)`, then
commits value one.

## Reconstruction boundary

`components/apollo_main/core_overlay/uled_display_preprocess.c` is an
independently authored one-entry candidate (5,405 bytes, SHA-256
`2ded39fb95b869de5361340416b85d598194de8c7e7d90f57eefbbde8044b98b`).
Host tests pin all nine assertions, descriptor and region words, GPU-failure
behavior, source/offset conversion, and exact success-call order. Freestanding
compilation exposes exactly one global Thumb text symbol. The analyzer and
manifests pin the body, separate pool, template, retained strings, call root,
provider calls, false-call halfword, and raw-overlap exclusions.

The historical source revision and concrete GPU API names remain unresolved.
The candidate is absent from `overlay.json`; provider binding, placement,
redirects, and package verification remain pending, so it claims zero package
ownership bytes.
