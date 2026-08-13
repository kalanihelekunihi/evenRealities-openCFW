# Ambiq GPU-patch shadow-blur source-candidate audit

Status: bounded production-excluded clean-room candidate. This is one of the
six patch exports directly called by the recovered Ambiq LVGL subtree.

## Result

The exact AmbiqSuite 5.1.0 `lv_ambiq_shadow_blur_corner` section is 668 bytes,
has SHA-256 `cea1f3cb0efe575af62a887e8daec87479bc94807355f14df019cf02613faef8`,
and carries 39 relocations to eight unique public Nema functions. DWARF places
the entry at `ambiq_nema_extension.c:383`. Headless Ghidra analysis of that
exact relocatable object, followed by instruction-level argument checking,
recovers the complete command stream without depending on guessed stock
function boundaries.

The routine performs a separable two-pass box blur:

1. split the shadow width into an asymmetric leading width and half width;
2. extend texture one horizontally into texture two using three fitted blits;
3. clear texture one, select source-alpha accumulation, and add
   `leading + half` horizontally shifted samples with constant alpha
   `floor(255 / width)`;
4. repeat the extension vertically and accumulate `leading + half + 1`
   vertically shifted samples; and
5. restore the temporary clip.

The candidate exposes the exact blend modes, texture IDs, clips, clears,
constant color, and eight-coordinate blits through explicit callbacks. It
preserves the odd/even edge split and the width-one zero-horizontal/one-vertical
sample behavior.
Inputs inherit the binary contract: `shadow_width` must be positive and caller
geometry must make the fitted source rectangles valid.

Six focused tests pin odd, even, and width-one traces; the exact public section,
DWARF line, and relocation count; relocation-free Cortex-M55 hard-float output;
independent naming; documentation; and production exclusion.

Run:

```sh
make ambiq-gpu-patch-accessors-candidate
```

Production admission still requires comparison against captured Nema command
streams or rendered output on Apollo510 hardware. The candidate does not claim
textual identity with the unavailable implementation source.
