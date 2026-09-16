/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room recovery of LVGL's `lv_obj_init_draw_rect_dsc` body at
 * 0x00452616 in G2 firmware 2.2.6.10. Field offsets follow the stock G2
 * descriptor layout; control flow follows LVGL 9.3-dev `src/core/lv_obj_draw.c`.
 */

extern unsigned int open_cfw_runtime_obj_get_style_shadow_spread(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_shadow_color(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_shadow_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_text_color(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_text_font(
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
extern unsigned int open_cfw_retained_lv_image_src_get_type(const void *src);
extern void open_cfw_retained_memcpy(void *dst, const void *src, unsigned int len);
extern void open_cfw_retained_grad_memcpy(void *dst, const void *src, unsigned int len);

extern unsigned int open_cfw_retained_obj_get_style_radius(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_color(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_grad_color(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_grad_dir(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_main_stop(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_grad_stop(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_main_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_grad_opa(
    const void *obj,
    unsigned int part
);
extern const void *open_cfw_retained_obj_get_style_bg_grad(
    const void *obj,
    unsigned int part
);
extern const void *open_cfw_retained_obj_get_style_bg_image_src(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_image_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_image_recolor(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_image_recolor_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_bg_image_tiled(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_border_color(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_border_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_border_width(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_border_side(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_outline_width(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_outline_color(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_outline_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_outline_pad(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_shadow_width(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_shadow_offset_x(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_shadow_offset_y(
    const void *obj,
    unsigned int part
);

static unsigned int open_cfw_mix_opa(unsigned int style_opa, unsigned int layer_opa)
{
    return (style_opa * layer_opa) >> 8;
}

static void open_cfw_copy_color(void *dst, unsigned int color)
{
    open_cfw_retained_memcpy(dst, &color, 3U);
}

__attribute__((used, noinline))
void *open_cfw_runtime_obj_init_draw_rect_dsc(
    const void *obj,
    unsigned int part,
    unsigned int *draw_dsc,
    unsigned int passthrough
)
{
    draw_dsc[0] = (unsigned int)obj;
    draw_dsc[1] = part;

    unsigned char *bytes = (unsigned char *)draw_dsc;
    unsigned int layer_opa =
        open_cfw_retained_obj_draw_get_layer_opa(obj, part, draw_dsc);
    if (part == 0U || layer_opa > 2U) {
        draw_dsc[7] = open_cfw_retained_obj_get_style_radius(obj, part);

        if (bytes[0x20] != 0U) {
            bytes[0x20] =
                (unsigned char)open_cfw_retained_obj_get_style_bg_opa(obj, part);
            if (bytes[0x20] > 2U) {
                unsigned int bg_color =
                    open_cfw_retained_obj_get_style_bg_color(obj, part);
                bg_color = open_cfw_retained_obj_draw_normal_apply_layer_recolor(
                    obj, part, draw_dsc, bg_color
                );
                open_cfw_copy_color(bytes + 0x21, bg_color);

                const unsigned char *grad =
                    (const unsigned char *)open_cfw_retained_obj_get_style_bg_grad(
                        obj, part
                    );
                if (grad != (const unsigned char *)0 && (grad[11] & 0x0FU) != 0U) {
                    open_cfw_retained_grad_memcpy(draw_dsc + 9, grad, 12U);
                }
                else {
                    bytes[0x2f] = (unsigned char)(
                        (bytes[0x2f] & 0xF0U) |
                        (open_cfw_retained_obj_get_style_bg_grad_dir(obj, part) & 0x0FU)
                    );
                    if ((bytes[0x2f] & 0x0FU) != 0U) {
                        open_cfw_copy_color(draw_dsc + 9, bg_color);
                        unsigned int grad_color =
                            open_cfw_retained_obj_get_style_bg_grad_color(obj, part);
                        grad_color =
                            open_cfw_retained_obj_draw_normal_apply_layer_recolor(
                                obj, part, draw_dsc, grad_color
                            );
                        open_cfw_copy_color(bytes + 0x29, grad_color);
                        bytes[0x28] = (unsigned char)
                            open_cfw_retained_obj_get_style_bg_main_stop(obj, part);
                        bytes[0x2d] = (unsigned char)
                            open_cfw_retained_obj_get_style_bg_grad_stop(obj, part);
                        bytes[0x27] = (unsigned char)
                            open_cfw_retained_obj_get_style_bg_main_opa(obj, part);
                        bytes[0x2c] = (unsigned char)
                            open_cfw_retained_obj_get_style_bg_grad_opa(obj, part);
                    }
                }
            }
        }

        if (bytes[0x48] != 0U) {
            draw_dsc[17] =
                open_cfw_retained_obj_get_style_border_width(obj, part);
            if (draw_dsc[17] != 0U) {
                bytes[0x48] = (unsigned char)
                    open_cfw_retained_obj_get_style_border_opa(obj, part);
                if (bytes[0x48] > 2U) {
                    bytes[0x49] = (unsigned char)(
                        (bytes[0x49] & 0xE0U) |
                        (open_cfw_retained_obj_get_style_border_side(obj, part) & 0x1FU)
                    );
                    unsigned int border_color =
                        open_cfw_retained_obj_get_style_border_color(obj, part);
                    border_color =
                        open_cfw_retained_obj_draw_normal_apply_layer_recolor(
                            obj, part, draw_dsc, border_color
                        );
                    open_cfw_copy_color(bytes + 0x3e, border_color);
                }
            }
        }

        if (bytes[0x58] != 0U) {
            draw_dsc[20] =
                open_cfw_retained_obj_get_style_outline_width(obj, part);
            if (draw_dsc[20] != 0U) {
                bytes[0x58] = (unsigned char)
                    open_cfw_retained_obj_get_style_outline_opa(obj, part);
                if (bytes[0x58] > 2U) {
                    draw_dsc[21] =
                        open_cfw_retained_obj_get_style_outline_pad(obj, part);
                    unsigned int outline_color =
                        open_cfw_retained_obj_get_style_outline_color(obj, part);
                    outline_color =
                        open_cfw_retained_obj_draw_normal_apply_layer_recolor(
                            obj, part, draw_dsc, outline_color
                        );
                    open_cfw_copy_color(bytes + 0x4a, outline_color);
                }
            }
        }

        if (bytes[0x3b] != 0U) {
            draw_dsc[12] =
                (unsigned int)open_cfw_retained_obj_get_style_bg_image_src(obj, part);
            if (draw_dsc[12] != 0U) {
                bytes[0x3b] = (unsigned char)
                    open_cfw_retained_obj_get_style_bg_image_opa(obj, part);
                if (bytes[0x3b] > 2U) {
                    if (open_cfw_retained_lv_image_src_get_type(
                            (const void *)draw_dsc[12]
                        ) == 2U) {
                        draw_dsc[13] =
                            open_cfw_runtime_obj_get_style_text_font(obj, part);
                        unsigned int text_color =
                            open_cfw_runtime_obj_get_style_text_color(obj, part);
                        text_color =
                            open_cfw_retained_obj_draw_normal_apply_layer_recolor(
                                obj, part, draw_dsc, text_color
                            );
                        open_cfw_copy_color(draw_dsc + 14, text_color);
                    }
                    else {
                        unsigned int recolor =
                            open_cfw_retained_obj_get_style_bg_image_recolor(
                                obj, part
                            );
                        unsigned int recolor_opa =
                            open_cfw_retained_obj_get_style_bg_image_recolor_opa(
                                obj, part
                            );
                        unsigned int color32 =
                            open_cfw_retained_image_apply_layer_recolor(
                                obj, part, draw_dsc, recolor, recolor_opa
                            );
                        bytes[0x3c] = (unsigned char)(color32 >> 24);
                        unsigned int color = open_cfw_retained_lv_color_make(
                            (color32 >> 16) & 0xFFU,
                            (color32 >> 8) & 0xFFU,
                            color32 & 0xFFU
                        );
                        open_cfw_copy_color(draw_dsc + 14, color);
                        bytes[0x3d] = (unsigned char)
                            open_cfw_retained_obj_get_style_bg_image_tiled(obj, part);
                    }
                }
            }
        }

        if (bytes[0x6c] != 0U) {
            draw_dsc[23] =
                open_cfw_retained_obj_get_style_shadow_width(obj, part);
            if (draw_dsc[23] != 0U && bytes[0x6c] > 2U) {
                bytes[0x6c] =
                    (unsigned char)open_cfw_runtime_obj_get_style_shadow_opa(obj, part);
                if (bytes[0x6c] > 2U) {
                    draw_dsc[24] =
                        open_cfw_retained_obj_get_style_shadow_offset_x(obj, part);
                    draw_dsc[25] =
                        open_cfw_retained_obj_get_style_shadow_offset_y(obj, part);
                    draw_dsc[26] =
                        open_cfw_runtime_obj_get_style_shadow_spread(obj, part);
                    unsigned int shadow_color =
                        open_cfw_runtime_obj_get_style_shadow_color(obj, part);
                    shadow_color =
                        open_cfw_retained_obj_draw_normal_apply_layer_recolor(
                            obj, part, draw_dsc, shadow_color
                        );
                    open_cfw_copy_color(bytes + 0x59, shadow_color);
                }
            }
        }

        if (layer_opa < 0xFDU) {
            bytes[0x20] = (unsigned char)open_cfw_mix_opa(bytes[0x20], layer_opa);
            bytes[0x3b] = (unsigned char)open_cfw_mix_opa(bytes[0x3b], layer_opa);
            bytes[0x48] = (unsigned char)open_cfw_mix_opa(bytes[0x48], layer_opa);
            bytes[0x6c] = (unsigned char)open_cfw_mix_opa(bytes[0x6c], layer_opa);
            bytes[0x58] = (unsigned char)open_cfw_mix_opa(bytes[0x58], layer_opa);
        }
    }
    else {
        bytes[0x20] = 0U;
        bytes[0x3b] = 0U;
        bytes[0x48] = 0U;
        bytes[0x58] = 0U;
        bytes[0x6c] = 0U;
    }

    __asm__ volatile(
        ".rept 22\n"
        "nop\n"
        ".endr\n"
    );
    (void)passthrough;
    return draw_dsc;
}
