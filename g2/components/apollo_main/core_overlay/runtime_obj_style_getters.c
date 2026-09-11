/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of twenty generated LVGL 9.3
 * `LVGL/src/core/lv_obj_style_gen.c` getters at
 * 0x0043EEA6...0x0043EF70 in G2 firmware 2.2.6.10. Every one of them is a
 * thin two-argument-plus-constant forward to the shared style-lookup core
 * `lv_obj_get_style_prop` (FUN_0044BDEA, itself outside this item's
 * range), each passing a distinct `lv_style_prop_t` literal. Property IDs
 * are confirmed against the official LVGL 9.3-dev interval
 * 60d976c..344c7c (github.com/lvgl/lvgl) `src/misc/lv_style.h` enum,
 * which the G2 firmware is independently pinned to by
 * ../../../docs/research/lvgl-version-recovery-audit.md:
 *
 *   0x01 LV_STYLE_WIDTH               0x10 LV_STYLE_PAD_TOP
 *   0x02 LV_STYLE_HEIGHT               0x11 LV_STYLE_PAD_BOTTOM
 *   0x04 LV_STYLE_MIN_WIDTH            0x12 LV_STYLE_PAD_LEFT
 *   0x05 LV_STYLE_MAX_WIDTH            0x13 LV_STYLE_PAD_RIGHT
 *   0x06 LV_STYLE_MIN_HEIGHT           0x6C LV_STYLE_TRANSLATE_X
 *   0x07 LV_STYLE_MAX_HEIGHT           0x6D LV_STYLE_TRANSLATE_Y
 *   0x08 LV_STYLE_X                    0x6E LV_STYLE_TRANSFORM_SCALE_X
 *   0x09 LV_STYLE_Y                    0x6F LV_STYLE_TRANSFORM_SCALE_Y
 *   0x0A LV_STYLE_ALIGN                0x70 LV_STYLE_TRANSFORM_ROTATION
 *                                      0x71 LV_STYLE_TRANSFORM_PIVOT_X
 *                                      0x72 LV_STYLE_TRANSFORM_PIVOT_Y
 *
 * `lv_obj_get_style_align` (property 0x0A, at 0x0043EEF6) is two bytes
 * larger than its siblings because the stock compiler additionally
 * widens its bool-shaped return to match the caller's 8-bit read; the
 * source shape is otherwise identical, so it shares this file's shared
 * forwarding call.
 */

typedef unsigned int open_cfw_runtime_style_getter_pointer;

#ifndef OPEN_CFW_RUNTIME_STYLE_GETTER_CORE
typedef unsigned int (*open_cfw_runtime_style_getter_core_fn)(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part,
    unsigned int property
);
#define OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(obj, part, property) \
    (((open_cfw_runtime_style_getter_core_fn)(__UINTPTR_TYPE__)0x0044BDEBU)( \
        (obj), (part), (property) \
    ))
#endif

enum {
    OPEN_CFW_RUNTIME_STYLE_PROP_WIDTH = 0x01U,
    OPEN_CFW_RUNTIME_STYLE_PROP_HEIGHT = 0x02U,
    OPEN_CFW_RUNTIME_STYLE_PROP_MIN_WIDTH = 0x04U,
    OPEN_CFW_RUNTIME_STYLE_PROP_MAX_WIDTH = 0x05U,
    OPEN_CFW_RUNTIME_STYLE_PROP_MIN_HEIGHT = 0x06U,
    OPEN_CFW_RUNTIME_STYLE_PROP_MAX_HEIGHT = 0x07U,
    OPEN_CFW_RUNTIME_STYLE_PROP_X = 0x08U,
    OPEN_CFW_RUNTIME_STYLE_PROP_Y = 0x09U,
    OPEN_CFW_RUNTIME_STYLE_PROP_ALIGN = 0x0AU,
    OPEN_CFW_RUNTIME_STYLE_PROP_TRANSLATE_X = 0x6CU,
    OPEN_CFW_RUNTIME_STYLE_PROP_TRANSLATE_Y = 0x6DU,
    OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_SCALE_X = 0x6EU,
    OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_SCALE_Y = 0x6FU,
    OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_ROTATION = 0x70U,
    OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_PIVOT_X = 0x71U,
    OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_PIVOT_Y = 0x72U,
    OPEN_CFW_RUNTIME_STYLE_PROP_PAD_TOP = 0x10U,
    OPEN_CFW_RUNTIME_STYLE_PROP_PAD_BOTTOM = 0x11U,
    OPEN_CFW_RUNTIME_STYLE_PROP_PAD_LEFT = 0x12U,
    OPEN_CFW_RUNTIME_STYLE_PROP_PAD_RIGHT = 0x13U
};

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_width(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_WIDTH
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_min_width(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_MIN_WIDTH
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_max_width(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_MAX_WIDTH
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_height(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_HEIGHT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_min_height(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_MIN_HEIGHT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_max_height(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_MAX_HEIGHT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_x(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_X
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_y(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_Y
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_align(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_ALIGN
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_translate_x(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_TRANSLATE_X
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_translate_y(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_TRANSLATE_Y
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_transform_scale_x(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_SCALE_X
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_transform_scale_y(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_SCALE_Y
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_transform_rotation(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_ROTATION
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_transform_pivot_x(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_PIVOT_X
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_transform_pivot_y(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_TRANSFORM_PIVOT_Y
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_pad_top(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_PAD_TOP
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_pad_bottom(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_PAD_BOTTOM
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_pad_left(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_PAD_LEFT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_pad_right(
    open_cfw_runtime_style_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(
        obj, part, OPEN_CFW_RUNTIME_STYLE_PROP_PAD_RIGHT
    );
}

#undef OPEN_CFW_RUNTIME_STYLE_GETTER_CORE
