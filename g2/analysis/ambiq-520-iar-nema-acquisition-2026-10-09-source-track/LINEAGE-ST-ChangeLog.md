# NEMAP_1.4.17_20250625-SW (NemaGFX [1.4.17] - 2025-06, NemaVG [1.1.12] - 2025-06)

## Added

## Changed

## Fixed
- interpolating depth when z values are different at each vertex. Workaround for current HW (Z24_8 format)
- interpolating negative depth steps
- Collinear optimisation in stroking when lines have different direction

---

# NEMAP_1.4.15_20250508-SW (NemaGFX [1.4.15] - 2025-05, NemaVG [1.1.11] - 2025-05)

## Added

## Changed

## Fixed
- nema_fill_rounded_rect_aa: remove extra drawn triangle in corners for STM32U5A9 revision B
- Circular flag is set during bind stage not unbind
- Fix putting caps in zero paths when other parts of the path are drawn
- Reset end line information when a new subpath starts
- Do not draw a join between first and last line when they are not adjacent
- Clipped path writing incorrectly the user provided buffer size

---

# NEMAP_1.4.13_20250120-SW (NemaGFX [1.4.13] - 2025-01, NemaVG [1.1.9] - 2025-01)

## Added

- nema_enable_aa_flags: takes uint32_t aa flags as an argument
- nema_cmdlist: nema_cl_bind_sectored_circular()
  - bind a command list as a sectored circular that is, a circular with multiple sectors (subCLs)
- NEMA_ERR_INVALID_SECTORED_CL_SIZE
  - error when sectors of sectored CL are less than 512 bytes in size
- nema_vg_verify_path()
  - Verify a path's coordinates if valid
- nema_vg_bind_clip_coords_buffer()
  - new function for binding clipped data as float and clipped segments as unit8_t array
- nema_vg_bind_stencil_buffer_prealloc()
  - new function for binding new stencil buffer at runtime
- nema_vg_bind_stencil_pool()
  - new function for binding new stencil buffer at runtime
- nema_vg_bind_stencil()
  - new function for binding new stencil buffer at runtime
- nema_vg_stroke_set_dash_pattern
  - sets dash pattern
- nema_vg_stroke_set_dash_phase
  - sets dash phase
- nema_vg_stroke_reset_dash_phase
  - controls reset dash phase behaviour

## Changed

- nema_vg_font_t struct has extra member of "units_per_em"
- nema_vg_bind_clip_coords_buf
  - DEPRECATED
- nema_vg_draw_ring
  - function now follows the caps set by nema_vg_stroke_set_cap_style()

## Fixed

- nema_blender: perform masking with texture
- drawing coordinates outside nema hw limits when sw handling is enabled
- Vector font converter: generated font struct "units_per_em" field location
- miter limit calculation
- nema_vg_path_clear()
  - Clear path data and segs
- nema_vg_generate_raster_font()
  - Bugfix, incorrect bitmaps buffer clear
- nema_vg_tsvg_draw()
  - Use non-zero fill rule when rendering fonts with fill

---

# NEMAP_1.4.11_20240704-SW (NemaGFX [1.4.11] - 2024-06, NemaVG [1.1.7] - 2024-06)

## Added

- nema_vg_stroke_set_cap_style()     
  - Support for end/start stroke caps (BUTT/SQUARE/ROUND)
- nema_vg_stroke_set_join_style()
  - Support for stroke joins (BEVEL/ROUND/MITER)
- nema_vg_stroke_set_miter_limit
  - Support for mitter join limit
- nema_vg_generate_raster_font()
  - Generate a raster font from a vector font
- nema_vg_tsvg_disable_feature()
  - Disables a tsvg feature from drawing

## Changed

- nema_font: blending mode when rendering opaque characters
- nema_vg_paint_set_stroke_width() to nema_vg_stroke_set_width() nema_vg_paint_set_stroke_width() kept as DEPRECATED

---

# NEMAP_1.4.10_20240301-SW (NemaGFX [1.4.10] - 2024-02, NemaVG [1.1.6] - 2024-02)

## Added

- New blending operation: NEMA_BLOP_RECOLOR
- Support for multithread on circular command list
- provisional: nema_vg_thread_init() -Support for multiple threads in NemaVG
- nema_get_sw_device_name(): Function to return the name of the architecture for which the software has been compiled

## Fixed

- nema_font:      line width calculation
- nema_vg_font:   line width calculation
- nema_vg:        fixed NEMA_BLOP_SRC_CKEY mode with vg operations
- nema_cmdlist:   flush command lists we have branched/jumped to
- nema_graphics:  nema_reinit - preloaded shaders not loaded during reinit
- nema_vg_reinit: context stencil/lut buffer correct address after reinit
- AA issue in rotations (found in Tiger Ice cream demo, STMTCS-59)

---

# NEMAP_H23.10_S1.4.9_20231110-SW

##  Added

- nema_get_sw_device_name(): Function to return the name of the architecture for which the software has been compiled

## Fixed

- nema_reinit: preloaded shaders not loaded during reinit
- nema_vg_reinit: context stencil/lut buffer correct address after reinit
- AA issue in rotations (found in Tiger Icecream demo, STMTCS-59)

---

# NEMAP_H23.0.6_S1.4.8_20230703-SW

## Added

- nema_blit_quad_m
  - Blit function with a user provided matrix
- Support for NEMA_L1LE,NEMA_L2LE,NEMA_L4LE in lut's indices 

---

# NEMAP_S1.4.7_20230512-SW

## Added

- tsi_malloc: tsi_malloc_init_pool_aligned()
  - memory allocations in a pool are byte aligned
- Add error codes for missing init: NEMA_ERR_NO_INIT, NEMA_VG_ERR_NO_INIT
- nema_font: nema_string_indexed_get_bbox
  - get the bounding box of a string with indexed glyphs
- nema_font: nema_font_get_x_advance
  - get the bound font horizontal advance

## Fixed

- Correctly Flush CL buffer on circular CLs
- nema_provisional: fill_rounded_rect_corner() fix for RASTERIZER_BUG_WA flow 
- Conical gradient in stroked ellipse
- Broaden stencil dirty area on stencil clear
- Correct gradient buffer when clipping is enabled
- Bevel joins not showing when path closes implicitly
- Correct stroke width when multi-transformation matrix
- nema_font: blending: modulate alpha channel when alpha value is smaller than 255
- nema_font: nema_print_char_indexed - set blending mode and character color
