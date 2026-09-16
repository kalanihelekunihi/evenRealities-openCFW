/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room recovery of LVGL's `lv_obj_calculate_ext_draw_size` body at
 * 0x00452C66 in G2 firmware 2.2.6.10. The implementation mirrors the
 * upstream LVGL 9.3-dev arithmetic in `src/core/lv_obj_draw.c`: shadow extent,
 * outline extent, then transform width/height. The style accessors are still
 * the retained firmware entry points; this leaf only replaces the arithmetic
 * combiner.
 */

extern int open_cfw_retained_obj_get_style_transform_width(
    const void *obj,
    unsigned int part
);
extern int open_cfw_retained_obj_get_style_transform_height(
    const void *obj,
    unsigned int part
);
extern int open_cfw_retained_obj_get_style_outline_width(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_retained_obj_get_style_outline_opa(
    const void *obj,
    unsigned int part
);
extern int open_cfw_retained_obj_get_style_outline_pad(
    const void *obj,
    unsigned int part
);
extern int open_cfw_retained_obj_get_style_shadow_width(
    const void *obj,
    unsigned int part
);
extern int open_cfw_retained_obj_get_style_shadow_offset_x(
    const void *obj,
    unsigned int part
);
extern int open_cfw_retained_obj_get_style_shadow_offset_y(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_shadow_spread(
    const void *obj,
    unsigned int part
);
extern unsigned int open_cfw_runtime_obj_get_style_shadow_opa(
    const void *obj,
    unsigned int part
);

static int open_cfw_abs_i32(int value)
{
    return value < 0 ? -value : value;
}

static int open_cfw_max_i32(int left, int right)
{
    return left < right ? right : left;
}

__attribute__((used, noinline))
int open_cfw_runtime_obj_calculate_ext_draw_size(
    const void *obj,
    unsigned int part
)
{
    int size = 0;
    int shadow_width = open_cfw_retained_obj_get_style_shadow_width(obj, part);
    if (shadow_width != 0) {
        unsigned int shadow_opa =
            open_cfw_runtime_obj_get_style_shadow_opa(obj, part);
        if (shadow_opa > 2U) {
            int shadow_offset_x =
                open_cfw_retained_obj_get_style_shadow_offset_x(obj, part);
            int shadow_offset_y =
                open_cfw_retained_obj_get_style_shadow_offset_y(obj, part);
            shadow_width = shadow_width / 2 + 1;
            shadow_width +=
                (int)open_cfw_runtime_obj_get_style_shadow_spread(obj, part);
            shadow_width += open_cfw_max_i32(
                open_cfw_abs_i32(shadow_offset_x),
                open_cfw_abs_i32(shadow_offset_y)
            );
            size = open_cfw_max_i32(size, shadow_width);
        }
    }

    int outline_width = open_cfw_retained_obj_get_style_outline_width(obj, part);
    if (outline_width != 0) {
        unsigned int outline_opa =
            open_cfw_retained_obj_get_style_outline_opa(obj, part);
        if (outline_opa > 2U) {
            int outline_pad =
                open_cfw_retained_obj_get_style_outline_pad(obj, part);
            size = open_cfw_max_i32(size, outline_pad + outline_width);
        }
    }

    int transform_width =
        open_cfw_retained_obj_get_style_transform_width(obj, part);
    int transform_height =
        open_cfw_retained_obj_get_style_transform_height(obj, part);
    int transform = open_cfw_max_i32(transform_width, transform_height);
    if (transform > 0) {
        size += transform;
    }
    return size;
}
