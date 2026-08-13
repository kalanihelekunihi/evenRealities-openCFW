# Ambiq GPU-patch small-raster source-candidate audit

Status: bounded production-excluded clean-room candidates for two non-required
GPU-patch exports.

The exact 164-byte `lv_ambiq_create_corner_mask` section at source line 349
fixes a complete ten-effect pipeline: bind an A8 shadow texture, clear it,
clip below the shadow width, select opaque white, and rasterize a stroked arc
from 270 to 360 degrees before popping the clip. Its SHA-256 is
`6b1cbd72576ee8310eb7eab466570e6daa51a9446696ea8e748eea0088e0f95c`.

The exact 224-byte `lv_ambiq_l8_l4_convert` section at line 706 is a no-op for
odd widths. Even widths bind the half-width L4 destination, then render two
L8 source interpretations using x scales 4, translations -2/0, formats
`0x34`/`0x35`, blend modes 1/`0x10000101`, and texture/constant colors. Its
SHA-256 is `180127efa5ccd439952423bbd6dbde4123c59c574fd367f0c808a37ea0643bbe`.

Six tests pin both traces, odd-width behavior, exact section identities,
relocation-free Cortex-M55 text, independent naming, and production exclusion.
Both candidates express Nema operations through explicit ports. Neither export
is called by the recovered Ambiq LVGL subtree.
