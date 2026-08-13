# G2 ULED manager recovery

Status: complete linked-object census and panel-selection/dispatch ABI closure;
historical source, clean-room implementation, and production routing pending.
Run addresses use `run = file_offset + 0x00437FE0`.

## Result

The retained first-party path `driver\uled\drv_mspi_uled.c` owns the physical
interval `[0x004C9D44,0x004CA6F8)`. Fourteen linked bodies contribute 2,332
bytes with SHA-256
`502a7480281cb8beefe16a10a1a066fe7236712086eb01341c38c97161ee250e`.
Two alignment halfwords and the 148-byte literal pool contribute 152 bytes
with SHA-256
`e6519cf253e67cd737e6ccfa9f7533ec14380b6f1fc6ce5e3967acb1d8e6c813`.
The complete 2,484-byte object has SHA-256
`c0630c1686b6a9d6d10802f3620206a4cf73047a53d1aed00e4b079bb410c760`.

Every body was present in the authenticated discovered-function set. Exact
boundaries and hashes are pinned in
`tools/manifests/g2-uled-manager-function-map.tsv`.

## Linked surface

| Group | Functions |
|---|---|
| selection/lifecycle | `uled_mspi_term`, `uled_driver_identify`, `uled_mspi_init`, `uled_driver_init` |
| panel wrappers | `uled_clearScreen`, `uled_safe_get_chip_id`, power down/up, brightness, display offset, async refresh, status/recovery, set mode |
| framebuffer helper | `uled_clean_fb_data` |

The retained function-name strings agree with the current bodies. The sole
name without a retained function string, `uled_mspi_term`, is descriptive and
follows directly from its offset-zero callback dispatch and startup
termination-table ingress. Historical decompilation is used only as naming
corroboration, not as a source or license oracle.

## Panel selection and operations ABI

The manager's linker list is the eight-byte object
`[0x0078EE24,0x0078EE2C)`, SHA-256
`2dfd9fd3eca94e66fbeecdd42d7dd6a26e54971d00dc7d50f2d68f028dbd63f0`.
It contains exactly two operations-record pointers:

| Pointer | Panel | Type at `+0x3C` |
|---:|---|---:|
| `0x0070AFE4` | Hongshi/A6N-G | 1 |
| `0x0070B024` | JBD4010 | 0 |

The selector reads configuration key one and converts its first byte to the
Boolean `byte == 0x06`. Thus value `0x06` selects type-one A6N-G; every other
value selects type-zero JBD4010. It scans at most three records but the
authenticated linker range contains exactly two. A successful match is stored
at active-operations pointer `0x20074530`; failure starts the one-unit timer
and returns `-1`.

Each record is 64 bytes:

| Offset | Callback/field |
|---:|---|
| `+0x00` | terminate |
| `+0x04` | read chip ID |
| `+0x08` | MSPI initialize |
| `+0x0C` | panel initialize |
| `+0x10/+0x14` | power up/down |
| `+0x18` | set brightness |
| `+0x1C` | clear screen |
| `+0x20` | set current |
| `+0x24` | set display offset |
| `+0x28/+0x2C` | asynchronous/blocking partial refresh |
| `+0x30` | status check and recovery |
| `+0x34` | set mode |
| `+0x38` | optional serial/die-ID reader |
| `+0x3C` | panel type/capability byte |

The JBD record leaves the last callback and type word zero. The A6N-G record
provides all 15 callbacks and type one. Their per-panel bytes and target
closures are independently pinned by the two panel audits.

## Initialization and wrapper behavior

`uled_mspi_init` selects the panel and calls operations `+0x08` with three
arguments: runtime Thumb callback `0x004CA2AD`, framebuffer pointer from
`0x200007B8`, and configuration object `0x203795A0`. The callback address is
materialized by the exact `addw r0,pc,#0x301` at `0x004C9FA8`; it is not a
stored literal. The panel driver retains that callback and invokes it before
full refresh.

The remaining wrappers guard the active record, log a retained diagnostic on
absence, and dispatch through the offsets above. Power-up/down additionally
require the selected callback to be non-null. Missing-driver return values are
normally `-1`; safe chip ID uses `0xFFFF`, while the status wrapper deliberately
returns zero. The terminate wrapper is rooted by the odd Thumb pointer at
startup table cell `0x00438090`.

## Packed framebuffer helper

`uled_clean_fb_data(value,x0,y0,x1,y1)` caps `x1` at 639 and `y1` at 479,
rejects reversed ranges, then fills the selected rectangle in the common
640x480 four-bit framebuffer. Each row is 320 bytes. Even/odd endpoint cases
preserve the untouched nibble at either boundary, while byte-aligned regions
are filled directly. This helper is the runtime callback supplied to both
panel drivers during MSPI initialization.

## Ingress closure

Eighteen direct BL sites reach exact manager entries: one internal selector
call and 17 exterior callers. The bodies contain 97 genuine direct calls.
Fifteen additional raw BL-looking windows in the nibble-fill routine are
multiply/VFP encodings and are pinned as explicit exclusions. No direct BL or
`B.W` reaches a strict body interior.

The only stored entry is the termination pointer at `0x00438090`. The clean
helper has the one runtime materialization described above. One
strict-interior-looking value at odd byte offset `0x0064CF7B` is an overlapping
data window rather than a pointer. After qualification, strict-interior
ingress is zero.

## Reconstruction boundary

No authenticated historical manager source is available, so no license or
whole-source identity is inferred. The current evidence pins the complete
linked object, selector, linker records, callback ABI, wrapper behavior,
framebuffer transform, and all entry forms. No manager source appears in
`overlay.json`; the stock package retains all 2,484 bytes and OpenCFW claims
zero production ownership. The exterior orchestration body at `0x00473C44`
is already independently source-owned as the display-manager receive loop;
the remaining ULED gap is therefore clean-room implementation and provider
validation for this retained manager and the other unavailable first-party
ULED objects, not attribution of that caller by address proximity.

Run the fail-closed audit and focused tests with:

```sh
python3 tools/analyze_g2_uled_manager.py
python3 -m unittest tests.test_analyze_g2_uled_manager
```
