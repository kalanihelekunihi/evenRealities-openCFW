/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room recovery of LVGL's `lv_obj_init_draw_label_dsc` body at
 * 0x00452988 in G2 firmware 2.2.6.10. The field offsets are the stock G2
 * descriptor layout observed in the authenticated body; the control flow is
 * the upstream LVGL 9.3-dev label draw-descriptor initializer.
 */

extern unsigned int open_cfw_runtime_obj_get_style_text_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_text_color(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_text_letter_space(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_text_line_space(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_text_decor(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_text_font(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_text_align(
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
void *open_cfw_runtime_obj_init_draw_label_dsc(
    const void *obj,
    unsigned int part,
    unsigned int *draw_dsc,
    unsigned int passthrough
)
{
    draw_dsc[0] = (unsigned int)obj;
    draw_dsc[1] = part;

    unsigned char *bytes = (unsigned char *)draw_dsc;
    unsigned int text_opa = open_cfw_runtime_obj_get_style_text_opa(obj, part);
    bytes[0x50] = (unsigned char)text_opa;
    if (bytes[0x50] > 2U) {
        unsigned int layer_opa =
            open_cfw_retained_obj_draw_get_layer_opa(obj, part, draw_dsc);
        if (layer_opa < 0xFDU) {
            bytes[0x50] = (unsigned char)open_cfw_mix_opa(bytes[0x50], layer_opa);
        }
        if (bytes[0x50] > 2U) {
            unsigned int text_color =
                open_cfw_runtime_obj_get_style_text_color(obj, part);
            unsigned int recolored =
                open_cfw_retained_obj_draw_normal_apply_layer_recolor(
                    obj, part, draw_dsc, text_color
                );
            open_cfw_retained_memcpy(draw_dsc + 9, &recolored, 3U);
            draw_dsc[11] =
                open_cfw_runtime_obj_get_style_text_letter_space(obj, part);
            draw_dsc[10] =
                open_cfw_runtime_obj_get_style_text_line_space(obj, part);
            bytes[0x53] = (unsigned char)(
                (bytes[0x53] & 0xF8U) |
                (open_cfw_runtime_obj_get_style_text_decor(obj, part) & 7U)
            );
            draw_dsc[8] =
                open_cfw_runtime_obj_get_style_text_font(obj, part);
            bytes[0x51] =
                (unsigned char)open_cfw_runtime_obj_get_style_text_align(obj, part);
        }
    }

    (void)passthrough;
    return draw_dsc;
}
