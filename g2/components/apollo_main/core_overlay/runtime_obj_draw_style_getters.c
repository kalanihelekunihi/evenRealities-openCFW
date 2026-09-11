/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of twenty-seven generated LVGL 9.3
 * `LVGL/src/core/lv_obj_style_gen.h` inline style getters at
 * 0x0045246E...0x0045260A in G2 firmware 2.2.6.10. Every one of them is the
 * same one-line body as its official counterpart:
 *
 *     lv_style_value_t v = lv_obj_get_style_prop(obj, part, LV_STYLE_XXX);
 *     return v.num;   /- or v.color / v.ptr, same bit pattern -/
 *
 * so each is a thin two-argument-plus-constant forward to the shared style
 * lookup core `lv_obj_get_style_prop` (FUN_0044BDEA at 0x0044BDEA, itself
 * outside this item's range and still stock -- it is AM-011's target
 * 0x0044B8AC..0x0044CAD8, tracked separately in remaining-work.md). This
 * file only owns the 27 constant-selecting forwards; it does not change
 * `lv_obj_get_style_prop` itself.
 *
 * Property IDs are confirmed against the official LVGL 9.3-dev interval
 * 60d976c..344c7c (github.com/lvgl/lvgl) `src/misc/lv_style.h` enum, which
 * the G2 firmware is independently pinned to by
 * ../../../docs/research/lvgl-version-recovery-audit.md, and against the
 * generated getter bodies in the same interval's
 * `src/core/lv_obj_style_gen.h`:
 *
 *   0x0C LV_STYLE_RADIUS               0x50 LV_STYLE_ARC_WIDTH
 *   0x3D LV_STYLE_SHADOW_COLOR         0x51 LV_STYLE_ARC_ROUNDED
 *   0x3E LV_STYLE_SHADOW_OPA           0x52 LV_STYLE_ARC_COLOR
 *   0x42 LV_STYLE_SHADOW_SPREAD        0x53 LV_STYLE_ARC_OPA
 *   0x44 LV_STYLE_IMAGE_OPA            0x54 LV_STYLE_ARC_IMAGE_SRC
 *   0x45 LV_STYLE_IMAGE_RECOLOR        0x58 LV_STYLE_TEXT_COLOR
 *   0x46 LV_STYLE_IMAGE_RECOLOR_OPA    0x59 LV_STYLE_TEXT_OPA
 *   0x48 LV_STYLE_LINE_WIDTH           0x5A LV_STYLE_TEXT_FONT
 *   0x49 LV_STYLE_LINE_DASH_WIDTH      0x5B LV_STYLE_TEXT_LETTER_SPACE
 *   0x4A LV_STYLE_LINE_DASH_GAP        0x5C LV_STYLE_TEXT_LINE_SPACE
 *   0x4B LV_STYLE_LINE_ROUNDED         0x5D LV_STYLE_TEXT_DECOR
 *   0x4C LV_STYLE_LINE_COLOR           0x5E LV_STYLE_TEXT_ALIGN
 *   0x4D LV_STYLE_LINE_OPA             0x62 LV_STYLE_OPA
 *                                      0x69 LV_STYLE_BLEND_MODE
 *
 * Every stock body in this span is either 10 bytes (a tail call that just
 * forwards `lv_obj_get_style_prop`'s r0 untouched -- Ghidra shows it as
 * `void`) or 12/22/32 bytes (a non-tail call whose decompilation shows the
 * same r0 result copied into a wider `undefined8` return because Ghidra
 * cannot tell a bare `int32_t`/pointer-shaped result from a 3-byte
 * `lv_color_t` one at this call site). Both shapes return exactly what
 * `lv_obj_get_style_prop` returned in r0 with no other computation, so this
 * file models every one of the 27 with a single `unsigned int` return type
 * -- the same simplification already used by the analogous
 * `runtime_obj_style_getters.c` layout-property tranche for the same
 * `lv_obj_get_style_prop` core -- and lets callers reinterpret the result as
 * a signed int, a `const void *`, or the low three bytes of an
 * `lv_color_t` as the upstream header does per property.
 */

extern unsigned int open_cfw_retained_obj_get_style_prop(
    const void *obj,
    unsigned int part,
    unsigned int prop
);

enum {
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_RADIUS = 0x0CU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_SHADOW_COLOR = 0x3DU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_SHADOW_OPA = 0x3EU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_SHADOW_SPREAD = 0x42U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_IMAGE_OPA = 0x44U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_IMAGE_RECOLOR = 0x45U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_IMAGE_RECOLOR_OPA = 0x46U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_WIDTH = 0x48U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_DASH_WIDTH = 0x49U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_DASH_GAP = 0x4AU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_ROUNDED = 0x4BU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_COLOR = 0x4CU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_OPA = 0x4DU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_WIDTH = 0x50U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_ROUNDED = 0x51U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_COLOR = 0x52U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_OPA = 0x53U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_IMAGE_SRC = 0x54U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_COLOR = 0x58U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_OPA = 0x59U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_FONT = 0x5AU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_LETTER_SPACE = 0x5BU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_LINE_SPACE = 0x5CU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_DECOR = 0x5DU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_ALIGN = 0x5EU,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_OPA = 0x62U,
    OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_BLEND_MODE = 0x69U
};

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_shadow_spread(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_SHADOW_SPREAD
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_shadow_color(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_SHADOW_COLOR
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_shadow_opa(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_SHADOW_OPA
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_image_opa(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_IMAGE_OPA
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_image_recolor(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_IMAGE_RECOLOR
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_image_recolor_opa(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_IMAGE_RECOLOR_OPA
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_line_width(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_WIDTH
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_line_dash_width(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_DASH_WIDTH
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_line_dash_gap(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_DASH_GAP
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_line_rounded(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_ROUNDED
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_line_color(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_COLOR
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_line_opa(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_LINE_OPA
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_arc_width(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_WIDTH
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_arc_rounded(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_ROUNDED
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_arc_color(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_COLOR
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_arc_opa(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_OPA
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_arc_img_src(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_ARC_IMAGE_SRC
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_text_color(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_COLOR
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_text_opa(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_OPA
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_text_font(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_FONT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_text_letter_space(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_LETTER_SPACE
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_text_line_space(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_LINE_SPACE
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_text_decor(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_DECOR
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_text_align(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_TEXT_ALIGN
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_radius(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_RADIUS
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_opa(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_OPA
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_style_blend_mode(
    const void *obj,
    unsigned int part
)
{
    return open_cfw_retained_obj_get_style_prop(
        obj, part, OPEN_CFW_RUNTIME_DRAW_STYLE_PROP_BLEND_MODE
    );
}
