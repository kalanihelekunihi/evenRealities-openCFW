# Ambiq LVGL draw backend authenticated source snapshot

This directory preserves the byte-exact `src/draw/ambiq` subtree recovered
for the G2 Apollo main image. The canonical public source is AmbiqMicro's LVGL
repository at commit `5be8e0ae5077aa3880aba8a322b1487d6bc73c07`;
the imported subtree has Git tree
`1e774257495fa43177e04fc5c8a42a77c2d7d619`, 16 files, and 170,833 bytes.
The source is covered by the unchanged upstream `LICENCE.txt`.

`g2/tools/manifests/g2-lvgl-ambiq-source-provenance.json` pins each source
and header by byte count, Git blob SHA-1, and SHA-256. The firmware evidence
authenticates 11 of the 14 translation units as linked by G2; `border`, `line`,
and `vector` are retained only because they are members of the exact public
subtree and are not selected by the qualification builder.

The files below `src/draw/ambiq` are immutable upstream evidence. Compatibility
changes live separately below `g2-compat` and are applied only to a temporary
staging tree by `g2/tools/build_g2_lvgl_ambiq_backend.py`. That directory also
preserves the exact LVGL 9.3-development software-mask reference and a bounded,
per-parameter radius-mask provider for the authenticated cache-free G2
`lv_global_t` layout. The target gate compiles 11 backend objects plus that
provider, pins the two box-shadow call relocations, and uses the 32 KiB
draw-thread stack recovered from stock machine code.

This directory is not registered in a production overlay. A successful
isolated Cortex-M55 compile does not establish Nema archive linkage,
draw-thread runtime sufficiency, or live Apollo510 behavior.

Run the offline identity gate:

```sh
python3 g2/tools/build_g2_lvgl_ambiq_backend.py --json
```

Run the isolated target compile gate, when `clang` supports
`arm-none-eabi`/Cortex-M55:

```sh
python3 g2/tools/build_g2_lvgl_ambiq_backend.py --output-dir /tmp/g2-lvgl-ambiq
```
