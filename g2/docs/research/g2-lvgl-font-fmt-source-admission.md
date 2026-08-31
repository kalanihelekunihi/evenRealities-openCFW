# G2 LVGL fmt_txt bitmap source admission

## Result

The isolated Apollo/LVGL atomic link now has a zero-import, exact-ABI provider
for `lv_font_get_bitmap_fmt_txt`. It reproduces the authenticated LVGL
plain, byte-aligned, and compressed fmt_txt decoding algorithms, bounds every
write against the caller-owned draw buffer, keeps RLE state invocation-local,
and dispatches cache flush only through the caller-supplied draw-buffer
handler. It does not allocate heap storage or claim LVGL global, scheduler,
cache, MMIO, or hardware ownership.

The authenticated source is LVGL commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`. The pinned source blobs are:

- `src/font/lv_font_fmt_txt.c`: `53a927439f4af90cf5a3d591663f4098f22fea16`
- `src/font/lv_font_fmt_txt.h`: `f534b8abe5b4d2b76f5d7b6f4f06ac1229625802`
- `src/font/lv_font_fmt_txt_private.h`: `66df402d6b932029a6c2e67a635b207e6643cafc`
- `src/draw/lv_draw_buf_private.h`: `a22640315e37433b77605d4ac8f36e689d3b5e9c`

## Deterministic closure

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| target source object | 4,176 | `000a0c4bc5bd8ca6886b6a821f3cdbbbfd331d67a12b4a3a87e3581aaed6a8a4` |
| isolated provider | 4,688 | `9d4333cf6277960f46d5ce5e0cb8ef0b49e203861bb275afbcf7e409a789ef66` |
| ABI probe | 1,016 | `adad17c030719f3bc67ab0b525ea303221fb941caeadc0ab87d053588bef195e` |

The provider exports only `lv_font_get_bitmap_fmt_txt`, has no undefined ELF
symbols or external relocations, and closes the exact MOVW/MOVT address pair in
`lv_draw_ambiq_letter.o`. The host oracle checks raw access, unaligned and
byte-aligned 1-bpp rows, 2/4/8-bpp plain data, compressed 2-bpp rows with and
without the LVGL XOR prefilter, cache callback count, and malformed descriptor,
stride, capacity, and bpp failures under ASan and UBSan.

This moves the maximal residual from 16 to 15 symbols, digest
`4bf298c118bc54902862e938211a665f5edccd2be450dbad02323d4868680da5`.
The scoped external partial link is 1,368,580 bytes with SHA-256
`41631dcfe332ea964bab053d3d67785d54606e1afc2396a35cdda3d40fdfcd3b`.

## Evidence boundary

The fmt_txt ABI provides a bitmap pointer and per-glyph bitmap offset but no
bitmap blob length or glyph-descriptor count. The provider can therefore bound
all output writes, but input blob extent and glyph index validity remain caller
preconditions exactly as they are upstream. Production routing stays false
until font-asset lifetime and extent, draw-buffer handler initialization,
provider collision, RAM/flash placement, cache behavior, concurrency, and
hardware output are qualified. No authorized hardware evidence was available.
