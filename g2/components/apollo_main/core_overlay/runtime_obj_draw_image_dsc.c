/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room recovery of LVGL's `lv_obj_init_draw_image_dsc` body at
 * 0x00452A34 in G2 firmware 2.2.6.10. Field offsets follow the stock G2
 * descriptor layout; control flow follows LVGL 9.3-dev `src/core/lv_obj_draw.c`.
 */

typedef __UINTPTR_TYPE__ open_cfw_uintptr;

extern unsigned int open_cfw_runtime_obj_get_style_image_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_image_recolor(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_image_recolor_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_blend_mode(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_draw_get_layer_opa(
    const void *obj,
    unsigned int part,
    void *base_dsc
);
extern unsigned int open_cfw_retained_image_apply_layer_recolor(
    const void *obj,
    unsigned int part,
    void *base_dsc,
    unsigned int color,
    unsigned int recolor_opa
);
extern unsigned int open_cfw_retained_lv_color_make(
    unsigned int red,
    unsigned int green,
    unsigned int blue
);
extern int open_cfw_retained_lv_area_get_width(const void *area);
extern int open_cfw_retained_lv_area_get_height(const void *area);
extern void open_cfw_retained_memcpy(void *dst, const void *src, unsigned int len);

static unsigned int open_cfw_mix_opa(unsigned int style_opa, unsigned int layer_opa)
{
    return (style_opa * layer_opa) >> 8;
}

__attribute__((used, noinline))
void *open_cfw_runtime_obj_init_draw_image_dsc(
    const void *obj,
    unsigned int part,
    unsigned int *draw_dsc,
    unsigned int passthrough
)
{
    draw_dsc[0] = (unsigned int)obj;
    draw_dsc[1] = part;

    unsigned char *bytes = (unsigned char *)draw_dsc;
    unsigned int image_opa = open_cfw_runtime_obj_get_style_image_opa(obj, part);
    bytes[0x50] = (unsigned char)image_opa;
    if (bytes[0x50] > 2U) {
        unsigned int layer_opa =
            open_cfw_retained_obj_draw_get_layer_opa(obj, part, draw_dsc);
        if (layer_opa < 0xFDU) {
            bytes[0x50] =
                (unsigned char)open_cfw_mix_opa(bytes[0x50], layer_opa);
        }
        if (bytes[0x50] > 2U) {
            draw_dsc[12] = 0U;
            draw_dsc[13] = 0x100U;
            draw_dsc[14] = 0x100U;

            const void *coords = (const void *)((open_cfw_uintptr)obj + 0x14U);
            draw_dsc[17] =
                (unsigned int)(open_cfw_retained_lv_area_get_width(coords) / 2);
            draw_dsc[18] =
                (unsigned int)(open_cfw_retained_lv_area_get_height(coords) / 2);

            unsigned int recolor =
                open_cfw_runtime_obj_get_style_image_recolor(obj, part);
            unsigned int recolor_opa =
                open_cfw_runtime_obj_get_style_image_recolor_opa(obj, part);
            unsigned int color32 =
                open_cfw_retained_image_apply_layer_recolor(
                    obj, part, draw_dsc, recolor, recolor_opa
                );
            bytes[0x4f] = (unsigned char)(color32 >> 24);
            unsigned int color = open_cfw_retained_lv_color_make(
                (color32 >> 16) & 0xFFU,
                (color32 >> 8) & 0xFFU,
                color32 & 0xFFU
            );
            open_cfw_retained_memcpy(draw_dsc + 19, &color, 3U);

            if (part != 0U) {
                unsigned int blend_mode =
                    open_cfw_runtime_obj_get_style_blend_mode(obj, part) & 7U;
                bytes[0x51] = (unsigned char)((bytes[0x51] & 0xF8U) | blend_mode);
            }
        }
    }

    (void)passthrough;
    return draw_dsc;
}
