/* g2c: stand-in for Ambiq's non-public gpu_patch.h, used by the upstream
 * ambiq-lvgl draw units (profile g2-apollo-main-57). The two pattern-texture
 * helpers are the g2 reconstructions in
 * graphics/a-68-ambiq-gpu-patch/ambiq_gpu_patch.c (stock 0x5fa238 / 0x5fa7c0).
 * Prototypes match the stock call sites (wave20 disasm): the gradient calls at 0x53de06
 * and 0x53eaa6 pass r0=count, r1=sp+28 (stops), r2=sp+72 (colors), r3=#1 (NEMA_TEX1);
 * the dash line call at 0x53ef2e passes r0=[r4,#52], r1=[r4,#56], r2=color, r3=#1.
 * They also match the definitions in ambiq_gpu_patch.c and the upstream ambiq-lvgl callers. */
#ifndef G2C_GPU_PATCH_H
#define G2C_GPU_PATCH_H
#include <stdint.h>
#include "nema_interpolators.h"
void lv_ambiq_gradient_create_5fa238(int32_t count, const float *stops,
                                     const color_var_t *colors, uint32_t tex);
void lv_ambiq_dashline_create_5fa7c0(uint32_t dash_width, uint32_t dash_gap, uint32_t color,
                                     uint32_t tex);
#define lv_ambiq_gradient_create(n, s, c, t) \
    lv_ambiq_gradient_create_5fa238((int32_t)(n), (const float *)(s), (const color_var_t *)(c), (uint32_t)(t))
#define lv_ambiq_dashline_create(w, g, c, t) \
    lv_ambiq_dashline_create_5fa7c0((uint32_t)(w), (uint32_t)(g), (uint32_t)(c), (uint32_t)(t))
#endif
