# OpenCFW Ambiq LVGL boundary candidates

This directory holds independently named, production-excluded source
candidates for the proprietary-layout boundary between the recovered Ambiq
LVGL subtree and the public binary-only GPU extension.

`runtime_ambiq_gpu_patch_accessors_candidate.c` implements three relocation-
free accessors recovered from the exact AmbiqSuite 5.1.0 `gpu_patch.a` DWARF
and machine code. It is MIT clean-room code; it is not copied from,
linked as, or presented as the BSD-3-Clause archive implementation.

`runtime_ambiq_gpu_patch_dashline_candidate.c` closes the exact dash/gap
texture algorithm over explicit width, clip, blend, color, rectangle, and pop
ports. Both the exact public GCC section and stock IAR span qualify it.

`runtime_ambiq_gpu_patch_get_glyph_candidate.c` closes UTF-8 decoding and the
sentinel-terminated NemaVG font-range lookup using public font layouts and the
exact archive body.

`runtime_ambiq_gpu_patch_shadow_blur_candidate.c` closes the exact separable
two-pass shadow command stream, including its asymmetric odd/even margins and
different horizontal/vertical sample counts, over explicit Nema ports.

`runtime_ambiq_gpu_patch_gradient_candidate.c` closes the final recovered-LVGL
dependency over G2's exact two-stop boundary. Its endpoint, implicit-segment,
duplicate, and invalid-order behavior is qualified against exact-object
emulation.

`runtime_ambiq_gpu_patch_small_raster_candidate.c` closes the non-required A8
corner-mask arc and even-width L8/L4 two-pass conversion exports.

`runtime_ambiq_gpu_patch_shadow_blur_vg_candidate.c` closes the non-required
radial VG shadow path, including exact texture-zero and clip restoration.

Run `make ambiq-gpu-patch-accessors-candidate`. The full checkout records the
evidence and production gates in the seven
`g2/docs/research/ambiq-gpu-patch-*-source-candidate-audit.md` chronology files.
Research chronology is intentionally excluded from the official-payload-free
community archive; the candidate source and its software tests remain included.
