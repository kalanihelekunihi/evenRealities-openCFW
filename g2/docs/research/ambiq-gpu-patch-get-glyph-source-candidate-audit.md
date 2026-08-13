# Ambiq GPU-patch glyph-lookup source-candidate audit

Status: bounded production-excluded clean-room candidate. This export is not a
direct dependency of the recovered Ambiq LVGL subtree, but closing it reduces
the exact binary-only patch surface.

## Result

The exact AmbiqSuite 5.1.0 `lv_ambiq_get_glyph` section is 188 bytes, has
SHA-256 `73c9856b02da209dbe68f4985f79cee430c4bea04dfadd66cd22b2b44b191205`,
and carries only one relocation: `utf8_codepoint_size`. DWARF names:

- public entry at `ambiq_nema_extension.c:818`;
- inlined `get_codepoint` at line 761; and
- inlined `nema_get_codepoint_range` at line 801.

The recovered behavior is complete:

1. classify a one-to-four-byte UTF-8 sequence through the external size seam;
2. decode the scalar with `0x7F`, `0x1F/0x3F`, `0x0F/0x3F`, or
   `0x07/0x3F` masks;
3. reject invalid widths and codepoint zero;
4. walk `font->ranges` until a range whose glyph pointer is null;
5. for an inclusive match, return `glyphs[codepoint - first]`.

The public NemaVG font header independently fixes a 36-byte glyph record,
12-byte range, and `font->ranges` at `+0x04` on Apollo5. The GCC instruction
sequence multiplies the glyph index by 36, exactly corroborating that ABI.

The clean-room candidate passes six focused tests: all four UTF-8 widths,
inclusive range boundaries, missing-range sentinel termination, invalid width,
zero codepoint, exact section/DWARF/relocation evidence, 32-bit target layout,
relocation-free Cortex-M55 output, independent naming, and production
exclusion. Its size-classification dependency is an explicit callback rather
than a hidden link to the binary Nema utility.

Run:

```sh
make ambiq-gpu-patch-accessors-candidate
```

Production admission would still require selection of the exact Nema UTF-8
classification policy, malformed-input policy review, and integration tests
against real vector-font assets. The candidate does not claim textual identity
with unavailable source.

