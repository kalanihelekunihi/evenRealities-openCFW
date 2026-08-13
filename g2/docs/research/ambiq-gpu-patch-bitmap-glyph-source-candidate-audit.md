# Ambiq GPU-patch bitmap-glyph source-candidate audit

Status: bounded production-excluded clean-room candidate; not called by the
recovered Ambiq LVGL subtree.

The exact 1,036-byte section at source line 590, public 76-byte descriptor, 34
relocations, DWARF locals, and complete headless decompile recover four rendering paths:
direct aligned source binding, a packed-row one-line blit,
32-bit-aligned/2,046-pixel temporary staging, and rotated quad rendering.
The section SHA-256 is
`37ad8ca8a082a00d04feae707022535448d1920940335db4819130901c47f0a1`.

The candidate preserves format-specific bit widths, automatic stride,
rotation modulo 3,600, chunk overlap/alignment, temporary-buffer signaling,
opaque/non-opaque blend modes, matrix inversion, and quad transformation.
Seven tests cover all four paths, exact evidence, relocation-free target text,
independent naming, and production exclusion. Hardware rendering remains the
production gate.
