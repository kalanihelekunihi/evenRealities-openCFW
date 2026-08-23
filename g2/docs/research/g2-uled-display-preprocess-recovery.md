# G2 ULED display preprocessing recovery

Status: complete linked-object census and host/Thumb-qualified clean-room
candidate; production-routed into the Apollo main overlay. Run addresses use
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

## Production routing

The candidate is production-routed under the reviewed apple-clang profile.
Provider binding maps the candidate's abstract GPU seams onto the retained
stock providers exactly as the stock body's call sequence does: GPU start at
`0x004B092A`, the destination-channel configure/mode/enable providers at
`0x004B0730`/`0x004B1A78`/`0x004B0748`, the source-configuration provider at
`0x004B1608`, the offset provider at `0x004B1B48`, and the commit provider at
`0x004B0C8A`. The assertion-diagnostic sink is compiled out by the pinned
`-DOPEN_CFW_ULED_ASSERT` no-op fail-stop binding (the stock logger's
per-assertion line numbers are not recoverable from the candidate's seams,
so the assertion log is treated as a diagnostic like the other closures do),
and the GPU-failure diagnostic binding stays inert. Placement appends one
relocated closure leaf to the overlay: 242 text bytes plus the 28-byte GPU
descriptor-template read-only closure and four alignment pad bytes. One
`B.W` entry redirect with NOP fill replaces the 584 stock body bytes at
`[0x0046C73C,0x0046C984)`; the discontiguous 64-byte pool at
`[0x0046CA74,0x0046CAB4)` stays retained stock data, and the sole direct
call at `0x0046CA64` reaches the leaf through the redirect. The reviewed
rodata local-name class in `tools/apollo_overlay.py` was extended to admit
Clang `.L__const.<function>.<variable>` constant-aggregate locals, the same
role the existing `.L.str[.N]` class plays for string literals.

Apple Clang 21 overlay/component/package sizes are `164790/3688186/4466680`
with SHA-256 `208d2190fb52b0d0ac107d6986b2b45b39d6b4adf5ae588644734680323637f1`,
`909db5b082addd4da1f0b4a94ae7fc43a506b3bb51ca56ac952d244d837c3b13`, and
`a79eebc34b8f514f89d9c7b85f50599321451a5c3473909b8f1abfe54f17fb4c`. The
leaf and redirect are gated `apple-clang`; the linux-clang profile keeps its
recorded pins, and linux-clang leaf pins await Linux toolchain regeneration.
Ownership is 584 replaced stock body bytes. The component build, source
package, `open_cfw verify`, and the fail-closed analyzer and manifest census
all pass. No package was signed or flashed and no hardware was accessed.
