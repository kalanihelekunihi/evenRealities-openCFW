/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room recovery of LVGL's `lv_obj_init_draw_line_dsc` body at
 * 0x00452B0E in G2 firmware 2.2.6.10. Field offsets follow the stock G2
 * descriptor layout; control flow follows LVGL 9.3-dev `src/core/lv_obj_draw.c`.
 */

extern unsigned int open_cfw_runtime_obj_get_style_line_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_line_width(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_line_color(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_line_dash_width(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_line_dash_gap(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_line_rounded(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_draw_get_layer_opa(
    const void *obj,
    unsigned int part,
    void *base_dsc
);
extern unsigned int open_cfw_retained_obj_draw_normal_apply_layer_recolor(
    const void *obj,
    unsigned int part,
    void *base_dsc,
    unsigned int color
);
extern void open_cfw_retained_memcpy(void *dst, const void *src, unsigned int len);

static unsigned int open_cfw_mix_opa(unsigned int style_opa, unsigned int layer_opa)
{
    return (style_opa * layer_opa) >> 8;
}

__attribute__((used, noinline))
void *open_cfw_runtime_obj_init_draw_line_dsc(
    const void *obj,
    unsigned int part,
    unsigned int *draw_dsc,
    unsigned int passthrough
)
{
    draw_dsc[0] = (unsigned int)obj;
    draw_dsc[1] = part;

    unsigned char *bytes = (unsigned char *)draw_dsc;
    unsigned int line_opa = open_cfw_runtime_obj_get_style_line_opa(obj, part);
    bytes[0x3c] = (unsigned char)line_opa;
    if (bytes[0x3c] > 2U) {
        unsigned int layer_opa =
            open_cfw_retained_obj_draw_get_layer_opa(obj, part, draw_dsc);
        if (layer_opa < 0xFDU) {
            bytes[0x3c] = (unsigned char)open_cfw_mix_opa(bytes[0x3c], layer_opa);
        }
        if (bytes[0x3c] > 2U) {
            draw_dsc[12] = open_cfw_runtime_obj_get_style_line_width(obj, part);
            if (draw_dsc[12] != 0U) {
                unsigned int color =
                    open_cfw_runtime_obj_get_style_line_color(obj, part);
                unsigned int recolored =
                    open_cfw_retained_obj_draw_normal_apply_layer_recolor(
                        obj, part, draw_dsc, color
                    );
                open_cfw_retained_memcpy(draw_dsc + 11, &recolored, 3U);
                draw_dsc[13] =
                    open_cfw_runtime_obj_get_style_line_dash_width(obj, part);
                if (draw_dsc[13] != 0U) {
                    draw_dsc[14] =
                        open_cfw_runtime_obj_get_style_line_dash_gap(obj, part);
                }
                unsigned int rounded =
                    open_cfw_runtime_obj_get_style_line_rounded(obj, part) & 1U;
                bytes[0x3d] = (unsigned char)((bytes[0x3d] & 0xFEU) | rounded);
                bytes[0x3d] = (unsigned char)(
                    (bytes[0x3d] & 0xFDU) | ((bytes[0x3d] & 1U) << 1)
                );
            }
        }
    }

    (void)passthrough;
    return draw_dsc;
}
