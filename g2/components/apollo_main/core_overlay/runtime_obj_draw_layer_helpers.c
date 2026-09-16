/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room recovery of LVGL's `lv_obj_draw.c` layer opacity and recolor
 * helpers at 0x00452DF0, 0x00452E22, and 0x00452E68 in G2 firmware 2.2.6.10.
 * Field offsets follow the stock G2 draw descriptor and layer layouts; control
 * flow follows LVGL 9.3-dev `src/core/lv_obj_draw.c`.
 */

extern unsigned int open_cfw_runtime_obj_get_style_opa(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_opa_recursive(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_style_apply_recolor(
    const void *obj,
    unsigned int part,
    unsigned int color
);
extern unsigned int open_cfw_retained_obj_get_style_recolor_recursive(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_lv_color_make(
    unsigned int red,
    unsigned int green,
    unsigned int blue
);
extern unsigned int open_cfw_retained_lv_color_mix(
    unsigned int color1,
    unsigned int color2,
    unsigned int mix
);
extern unsigned int open_cfw_retained_lv_color_to_32(
    unsigned int color,
    unsigned int opa
);
extern unsigned int open_cfw_retained_lv_color_over32(
    unsigned int fg,
    unsigned int bg
);

#if defined(OPEN_CFW_AM020_LAYER_OPA_ONLY)
static unsigned int open_cfw_mix_opa(unsigned int layer_opa, unsigned int style_opa)
{
    return (layer_opa * style_opa) >> 8;
}
#endif

static const void *open_cfw_draw_base_layer(const void *base_dsc)
{
    return *(const void * const *)((const unsigned char *)base_dsc + 0x10);
}

#if defined(OPEN_CFW_AM020_NORMAL_RECOLOR_ONLY) || \
    defined(OPEN_CFW_AM020_IMAGE_RECOLOR_ONLY)
static unsigned int open_cfw_layer_recolor32(
    const void *obj,
    unsigned int part,
    const void *base_dsc
)
{
    const void *layer = open_cfw_draw_base_layer(base_dsc);
    if (layer != 0) {
        unsigned int recolor =
            *(const unsigned int *)((const unsigned char *)layer + 0x39);
        if (part != 0U) {
            recolor =
                open_cfw_retained_obj_style_apply_recolor(obj, part, recolor);
        }
        return recolor;
    }

    return open_cfw_retained_obj_get_style_recolor_recursive(obj, part);
}
#endif

#if defined(OPEN_CFW_AM020_LAYER_OPA_ONLY)
__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_draw_get_layer_opa(
    const void *obj,
    unsigned int part,
    const void *base_dsc
)
{
    const void *layer = open_cfw_draw_base_layer(base_dsc);
    if (layer != 0) {
        unsigned int layer_opa =
            *(const unsigned char *)((const unsigned char *)layer + 0x38);
        if (part == 0U) {
            return layer_opa;
        }

        unsigned int style_opa = open_cfw_runtime_obj_get_style_opa(obj, part);
        unsigned int result = open_cfw_mix_opa(style_opa, layer_opa) & 0xffU;
        __asm__ volatile(
            ".rept 9\n"
            "nop\n"
            ".endr\n"
        );
        return result;
    }

    return open_cfw_retained_obj_get_style_opa_recursive(obj, part);
}
#endif

#if defined(OPEN_CFW_AM020_NORMAL_RECOLOR_ONLY)
__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_draw_normal_apply_layer_recolor(
    const void *obj,
    unsigned int part,
    const void *base_dsc,
    unsigned int color
)
{
    unsigned int recolor = open_cfw_layer_recolor32(obj, part, base_dsc);
    unsigned int recolor_color = open_cfw_retained_lv_color_make(
        recolor & 0xffU,
        (recolor >> 8) & 0xffU,
        (recolor >> 16) & 0xffU
    );
    unsigned int result = open_cfw_retained_lv_color_mix(
        recolor_color,
        color,
        (recolor >> 24) & 0xffU
    );
    __asm__ volatile(
        ".rept 9\n"
        "nop\n"
        ".endr\n"
    );
    return result;
}
#endif

#if defined(OPEN_CFW_AM020_IMAGE_RECOLOR_ONLY)
__attribute__((used, noinline))
unsigned int open_cfw_runtime_image_apply_layer_recolor(
    const void *obj,
    unsigned int part,
    const void *base_dsc,
    unsigned int color,
    unsigned int opa
)
{
    unsigned int recolor = open_cfw_layer_recolor32(obj, part, base_dsc);
    unsigned int recolor_opa = (recolor >> 24) & 0xffU;

    if (((opa & 0xffU) != 0U) && (recolor_opa != 0U)) {
        unsigned int base = open_cfw_retained_lv_color_to_32(color, opa);
        __asm__ volatile(
            ".rept 4\n"
            "nop\n"
            ".endr\n"
        );
        return open_cfw_retained_lv_color_over32(recolor, base);
    }
    if (recolor_opa != 0U) {
        __asm__ volatile(
            ".rept 4\n"
            "nop\n"
            ".endr\n"
        );
        return recolor;
    }
    __asm__ volatile(
        ".rept 3\n"
        "nop\n"
        ".endr\n"
    );
    return open_cfw_retained_lv_color_to_32(color, opa);
}
#endif
