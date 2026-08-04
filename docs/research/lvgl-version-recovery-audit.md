# G2 LVGL version, configuration, and source-boundary recovery

Status: read-only, production-excluded identity/configuration audit for the
official G2 `2.2.6.10` Apollo-main image. This tranche adds no LVGL snapshot,
overlay source, manifest entry, release pin, signer, programmer, or hardware
operation. The deterministic checker is
[`tools/analyze_g2_lvgl_version.py`](../../tools/analyze_g2_lvgl_version.py),
guarded by
[`tests/test_analyze_g2_lvgl_version.py`](../../tests/test_analyze_g2_lvgl_version.py).

## Result

The G2 stack is a vendor fork of the official **LVGL 9.3.0-development
lineage**, not an exact build of the released `v9.3.0` tag. Two independent
values stored by the complete G2 `lv_global_init` body narrow the compatible
official-mainline source state to:

| Boundary | Official LVGL commit | Date | Decisive state |
|---|---|---:|---|
| first compatible | `60d976c466e8619326edfbd193fd2a046c10113f` | 2025-03-25 | first official state with `LV_STYLE_LAST_BUILT_IN_PROP == 137` |
| last compatible | `344c7c318047b7348e1be8572a9fd4260c251cfa` | 2025-04-10 | last official state with `LV_EVENT_LAST == 66` |
| first excluded | `f35f0859eb477c79906cf531ed394306119097f8` | 2025-04-10 | adds `LV_EVENT_VSYNC_REQUEST`, changing `LV_EVENT_LAST` to 67 |

G2 stores `0x89` (137) as the last built-in style property and `0x42` (66)
as the last registered event. Immediately before `60d976c`, official LVGL
uses style sentinel 140. At `f35f0859`, official LVGL changes the event
sentinel from 66 to 67. The narrowest compatible unmodified-mainline interval
is therefore inclusive `60d976c..344c7c`.

This is a **source-equivalence interval**, not proof of one vendor checkout.
The Even/Ambiq fork could have branched earlier and cherry-picked changes, or
branched inside the interval and then modified files. No retained byte selects
one commit inside the interval. In particular, the mapped `lv_global_init`
and `lv_async` behavior and their reached ABI headers remain equivalent over
the interval. The only interval change to `lv_init.c` is in a deinitialization
configuration branch that does not distinguish the mapped G2 initializer.

## Why the `v9.3.0` tag is not exact

The directory label `third_party\lvgl_v9.3` is supporting evidence only. It
was not used as the version proof. The official release reference is:

| Item | Identity |
|---|---|
| annotated tag | `v9.3.0`, object `108e5aff3c90cc4d969331ed61aff2bbd365d430` |
| tag signature | no cryptographic signature embedded in the tag object |
| commit | `c033a98afddd65aaafeebea625382a94020fe4a7` |
| tree | `66bc30b9a8ecd144ba8b9ebfc984ac3028f55767` |
| commit date | 2025-06-03 13:57:17 +02:00 |
| version header blob | `8bbd5506ef8c8c298c3c761fb58d08633dfcb5a2` (`9.3.0`, empty info string) |

Three byte-visible facts exclude that release as the exact G2 source:

1. G2 stores `LV_EVENT_LAST == 66`; the tag has 67.
2. G2 embeds and uses the pre-refactor path
   `src/misc/cache/lv_cache_lru_rb.c`. Official commit
   `4b6dac865eea3c1d2ad253897fbaa9e0f758c5db` deletes/renames that file on
   2025-04-24, before the tag.
3. Both interval endpoints carry `lv_version.h` blob
   `6aa02efb6f0dae5919a86fe78532a9f8cee7fa01`, which advertises
   `9.3.0` with info string `"dev"`; the release tag carries a different
   blob with an empty info string.

The G2 initialization order also places `lv_freetype_init(64)` before the
generic and Ambiq draw initializers. That matches the official change at
`a4d70c9217092355df8c9aff5a730f166c82babf` and provides a looser independent
lower bound. The enum pair above is narrower.

## Exact official provenance available for reuse

Repository: <https://github.com/lvgl/lvgl.git>

The following content-addressed blobs are identical at both compatible
interval endpoints and are appropriate identity-pinned source inputs. Their
stability does not imply that the whole vendor tree is pristine.

| Official path | Git blob SHA-1 | Role |
|---|---|---|
| `LICENCE.txt` | `690d2dfd7e97ca8e06535a496761c5e81aece439` | MIT license |
| `lv_version.h` | `6aa02efb6f0dae5919a86fe78532a9f8cee7fa01` | `9.3.0-dev` identity |
| `src/core/lv_global.h` | `4515c01c9b80779a7d61701e28b4fb3554a92ba9` | global-state layout/config gates |
| `src/display/lv_display.c` | `695d38b2652decc2362b283dd69ee08b8b4f7582` | default display behavior and native-format assignment |
| `src/display/lv_display_private.h` | `d831ec4861e73f53da86432fb221804f71fa5c79` | display ABI |
| `src/draw/lv_draw_buf.h` | `c36e0a612f7fb46f69f5a7a4ae97000dd76a3837` | draw-buffer ABI |
| `src/misc/cache/lv_cache_lru_rb.c` | `be651dda9c22343444662acd204ec8a5ca37d516` | pre-refactor cache implementation |
| `src/misc/lv_async.c` | `b2e718dd3a3aefe274b6b962714c4e010bbd7f91` | exact async-call algorithm comparator |
| `src/misc/lv_event.h` | `ca52d18e454b745ea5302d32e5f49152de9e9643` | event sentinel 66 |
| `src/misc/lv_style.h` | `2da6cd1f8c903aebc142b473f4b1f846deb2073f` | style sentinel 137 |

The interval trees are
`37e23ad4b228c68133e3f65a8577c5028a4ea0c8` at the floor and
`2c76db856ec570f3ee12565181e5cf52bdd33d78` at the ceiling. A future source
snapshot may deliberately select the ceiling because it is the newest proven
compatible official state, but that would be an OpenCFW selection—not a claim
that Even used exactly that commit.

`src/misc/lv_color.h` changes for an unrelated reason within the interval, so
it is intentionally not mislabeled as a stable blob. Its pinned floor blob is
`c5ea01f82feb95f10e9c61788b42417477a1a51b` and its ceiling blob is
`1a160b4a56b8a7bc01b59a20b72ae35f5fff518c`. Both retain the decisive mapping
`LV_COLOR_DEPTH == 8` to `LV_COLOR_FORMAT_NATIVE == LV_COLOR_FORMAT_L8` (6).

### License

Official LVGL is MIT licensed. `LICENCE.txt` is 1,072 bytes, Git blob
`690d2dfd7e97ca8e06535a496761c5e81aece439`, SHA-256
`27a80bd36832ab42d35ad60c08b2b230a807a9bc0d58e94ec1531543dc49cbe8`.
This identity is stable across the proven interval and the `v9.3.0` tag.

## Conclusively mapped source behavior

Run addresses use `run = file_offset + 0x00437FE0`. Every complete span below
is authenticated before any semantic report is emitted.

| Boundary | Run interval | Bytes | SHA-256 |
|---|---:|---:|---|
| tick increment/get/elapsed cluster | `0x00473474..0x004734BC` | 72 | `4cd2008019ed18c308f6d25fe15694db454e820ce94991e8deeed9b815966c01` |
| `lv_global_init` | `0x004734CC..0x00473548` | 124 | `0354fab1a6d848856adb4017ad8343717f1c40bd59976b81526c7d4518b5c154` |
| `lv_init` | `0x00473548..0x00473626` | 222 | `864a6ef89d19b8f7dfb79aa84d4f85cf0df9fd1043a9f9104ad30c00c402fe33` |
| Ambiq display setup | `0x00473782..0x0047381E` | 156 | `d0f3a63dee7ba606340319bff6f4f094954e1834d3a60aac01e20e8732f13779` |
| `lv_display_create` | `0x0044F7C0..0x0044FA1A` | 602 | `1756df60b038522fdc9d2ac9681818f045db8a0dc2046fb4691a10a59d1472ad` |
| `lv_async_call` | `0x00484014..0x00484052` | 62 | `4a3b8927b10dd11d3b872207c2138dd85494060f948727dc021025c3b57c174f` |
| `lv_async_call_cancel` | `0x00484052..0x004840AA` | 88 | `67cd3979de3365531652c6de47f55bbab9541e753c5091a8423229635ce99900` |
| `lv_async_timer_cb` | `0x004840AC..0x004840C6` | 26 | `39c550823fd1d0bb1b80f29119c66bd33d2751de30c9d4c2ccc987bd99e5c8d8` |

The complete global initializer follows official `src/lv_init.c`:

- reject/assert a null global pointer;
- zero the complete global state;
- initialize display and input linked lists using the compiled object sizes;
- install the memory-zero sentinel, style-refresh flag, layout sentinel,
  style-property sentinel, and event sentinel; and
- seed the random state with `0x1234ABCD`.

The async cluster is source-equivalent to official `src/misc/lv_async.c` blob
`b2e718d`: it allocates the two-pointer `{callback,user_data}` record, creates
a zero-period timer, makes it one-shot, cancels every exact callback/data
match with delete-before-free ordering, and saves both fields before the timer
callback deletes/frees the record.

The G2 `lv_init` body retains the official initialization topology but inserts
an Ambiq draw/backend initializer. Therefore official `src/lv_init.c` is the
core algorithm comparator, not a byte-for-byte complete vendor translation
unit.

The complete G2 `lv_display_create` body clears the antialiasing flag and
stores byte value 6 in the display color-format field. Official interval blob
`695d38b` implements those operations as `LV_COLOR_DEPTH > 8` and
`LV_COLOR_FORMAT_NATIVE`, respectively. The two identity-pinned endpoint
`lv_color.h` blobs admit only `LV_COLOR_DEPTH == 8` for native ordinal 6.
This closes the color-depth inference without relying on the Ambiq port's
explicit format-6 buffer call alone.

## Recovered configuration and ABI

### Decisive compile-time configuration

| Setting | Recovered value | Binary evidence |
|---|---:|---|
| `LV_COLOR_DEPTH` | 8 | complete `lv_display_create` clears `LV_COLOR_DEPTH > 8` antialiasing and assigns native ordinal 6; both pinned endpoint headers uniquely map that pair to depth 8 |
| `LV_COLOR_FORMAT_NATIVE` | `LV_COLOR_FORMAT_L8` (6, 8 bpp) | complete `lv_display_create` assigns 6 to the official native-format field; Ambiq display independently creates its native buffer with format 6 |
| output format | `LV_COLOR_FORMAT_A4` (13, 4 bpp) | Ambiq output setup passes format 13 and exact 82,944-byte (`0x14400`) allocation = 576 × 288 / 2 |
| `LV_USE_OS` | `LV_OS_FREERTOS` | `src/osal/lv_freertos.c` survives inside its official `LV_OS_FREERTOS` compile guard; recursive semaphore/task paths are retained |
| `LV_USE_FREETYPE` | 1 | four guarded LVGL FreeType wrappers plus `lv_freetype_init(64)` |
| `LV_USE_FLEX` | 1 | guarded flex source path plus `LV_LAYOUT_LAST == 3` |
| `LV_USE_GRID` | 1 | guarded grid source path plus `LV_LAYOUT_LAST == 3`; both layouts are needed for sentinel 3 |
| `LV_USE_FS_LITTLEFS` | 1 | guarded `lv_fs_littlefs.c` path and initialization |
| `LV_USE_BMP` | 1 | guarded `lv_bmp.c` path |
| built-in binary decoder | retained | `lv_bin_decoder.c` path and init call; this interval does not gate the translation unit with an `LV_USE_BIN_DECODER` macro |
| `LV_USE_LOG` | 1 | warning/error calls retained |
| `LV_LOG_LEVEL` | warning | warning calls survive; `lv_init` INFO/TRACE calls compile out |
| `LV_USE_ASSERT_NULL` | 1 | null assertion/fatal sequence precedes the ordinary null return path |
| `LV_BIG_ENDIAN_SYSTEM` | 0 | little-endian runtime is accepted; the big-endian branch reaches the assertion/fatal hook |

Display setup is 576 by 288. This audit intentionally does not promote DPI,
task-notification selection, allocator hooks, every widget macro, or unused
draw switch to an exact configuration claim unless a distinct retained byte
proves it.

### Required target ABI assertions

| Type | G2 size | Evidence |
|---|---:|---|
| `lv_global_t` | `0x1EC` | complete size passed to the zeroing primitive |
| `lv_display_t` | `0x31C` | node size passed to display linked-list initialization |
| `lv_indev_t` | `0xDC` | node size passed to input linked-list initialization |
| `lv_draw_buf_t` | `0x1C` | Ambiq display-port state/draw-buffer allocation |
| `lv_async_info_t` | 8 | allocation size and two fields at offsets 0/4 |
| pointer | 4 | Cortex-M55 AAPCS and all recovered pointer layouts |
| enum ABI | short enums | interval reference compile reproduces the display/input sizes only with short enums, matching the IAR target ABI |

These are **vendor-configuration ABI gates**. They do not make an
unconfigured official checkout a safe drop-in. As an informative reference
compile, the official interval ceiling was compiled freestanding for
`arm-none-eabi`/Cortex-M55 with `-fshort-enums` and the public template
adjusted only to color depth 8 and flex/grid enabled. It reproduced both
version discriminators plus `sizeof(lv_display_t) == 0x31C`,
`sizeof(lv_indev_t) == 0xDC`, and `sizeof(lv_draw_buf_t) == 0x1C`. It produced
`lv_global_t == 0x1F8`, not G2's `0x1EC`, because the full G2 feature/port
configuration is not yet reconstructed. Without short enums the same headers
produce `lv_display_t == 0x324` and `lv_indev_t == 0xE8`. This is a useful
fail-closed result: the enum ABI is recovered, while the remaining global
size delta must close before broad linking against opaque callers.

## Source-path inventory and ownership split

The official image contains **78 unique paths** rooted under
`third_party\lvgl_v9.3`, not 76. The analyzer authenticates the entire image,
extracts every complete `.c` path, requires uniqueness, and classifies all 78:

| Classification | Paths | Source policy |
|---|---:|---|
| official LVGL core/standard/optional module | 61 | eligible for an authenticated interval snapshot plus recovered config |
| official LVGL FreeType wrapper | 4 | reuse as LVGL wrappers; keep actual FreeType provenance separate |
| Ambiq draw backend inside `LVGL/src/draw/ambiq` | 11 | vendor port; absent from official LVGL history |
| separate `lv_ambiq_display.c` | 1 | Ambiq display port, not LVGL core |
| separate `am_ftsystem.c` | 1 | Ambiq FreeType system glue, not LVGL or FreeType core |

The eleven Ambiq draw files include the backend root plus arc, buffer, fill,
image, letter, mask-rect, triangle, box-shadow, private, and vector-font
translation units. No official interval/tag tree contains those paths.

The four `LVGL/src/libs/freetype/lv_freetype*.c` files are official LVGL
wrappers. They do not establish the identity of the linked FreeType library.
The separately recovered FreeType boundary remains 2.9.1 plus Ambiq
`am_ftsystem.c` and Even's `app/gui/common/lvgl_font_manager.c` configuration.

First-party boundaries are independently pinned outside the third-party root:

- `platform/display_mgr/displaydrv_manager.c`;
- `platform/input/service_input_manager.c`;
- `app/gui/common/lvgl_font_manager.c`; and
- `app/gui/common/generic_animation.c`.

Even application/UI modules, display management, input transport, font-role
selection and animation policy must not be relabeled as upstream LVGL merely
because they call LVGL APIs.

## Recommended OpenCFW import boundary

The obvious open-source reuse is substantial, but it should remain layered:

1. Select and authenticate one official commit from the proven interval.
   `344c7c318047b7348e1be8572a9fd4260c251cfa` is the newest compatible choice,
   provided the project records that it is an OpenCFW baseline selection.
2. Import official core/misc/display/standard draw/widgets/layout and selected
   optional LVGL sources under the pinned MIT license.
3. Reconstruct `lv_conf.h` until all five ABI assertions above pass for the
   production compiler/short-enum settings.
4. Keep the eleven Ambiq draw files, `lv_ambiq_display.c`, `am_ftsystem.c`,
   actual FreeType, display manager, input and Even UI in separately licensed
   and tested port layers.
5. Treat movement from the interval to released `v9.3.0` as an explicit
   migration. At minimum it changes the event enum and cache subsystem and
   must not cross opaque G2 ABI boundaries without adapters.

The next focused disassembly work should target the remaining `lv_conf.h`
size deltas and Ambiq draw/display callback tables, not decompile the official
LVGL algorithms already covered by this interval.

## Remaining unknowns

- Exact Even/Ambiq fork commit or tree.
- Exact complete `lv_conf.h`, including task-notify, allocator/string hooks,
  draw-engine switches, unused widgets, cache counts, and task attributes.
- Whether vendor headers add fields beyond configuration-controlled official
  interval layouts; the reference size mismatch means this cannot be assumed
  away.
- Exact source/provenance for the eleven Ambiq draw files and display port.
- Exact migration adapters needed if OpenCFW chooses released `v9.3.0` or a
  newer maintained LVGL release instead of the compatibility interval.

No device was connected, signed, erased, programmed, or flashed.
