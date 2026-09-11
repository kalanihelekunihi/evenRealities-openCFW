/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of nine LVGL 9.3 `lv_obj_style.c` style-property
 * accessors retained in G2 firmware 2.2.6.10 inside AM-011's range
 * (0x0044B8AC..0x0044CAD8): the core getter `lv_obj_get_style_prop` at
 * 0x0044BDEA..0x0044BE4C and eight of its trivial single-property wrappers
 * at 0x0044B8AC..0x0044B90C.
 *
 * Identity evidence:
 *  - g2/tools/manifests/g2-lvgl-vendor-fork-census.tsv places every
 *    function in this cluster in LVGL/src/core/lv_obj_style.c by call
 *    topology (rows 0x0044B8AC..0x0044B902, "call-topology-single-file").
 *  - FUN_0044bdea (the wrappers' shared callee) branches to a fatal
 *    assert-log call on a NULL first argument that logs severity 3 at the
 *    literal source line 0x14c (332) -- the exact line of
 *    `LV_ASSERT_NULL(obj)` inside `lv_obj_get_style_prop()` in the
 *    vendored third_party/lvgl/src/core/lv_obj_style.c (LVGL v9.3.0
 *    snapshot pinned in this tree; see third_party/lvgl/README.openCFW.md
 *    for the upstream commit). It otherwise reads `*(ushort*)(obj+0x28)`
 *    (obj->state), ORs it with the `part` argument to form a selector,
 *    calls a helper taking (obj, selector, prop, &out) and returning a
 *    found/not-found byte (get_selector_style_prop, static in
 *    lv_obj_style.c, still retained at 0x0044CE8A), and on "not found"
 *    calls a one-argument default-value function
 *    (lv_style_prop_get_default, still retained at 0x0048297C). This is
 *    exactly the body of upstream `lv_obj_get_style_prop()`:
 *
 *        lv_style_value_t lv_obj_get_style_prop(const lv_obj_t *obj,
 *                                                lv_part_t part,
 *                                                lv_style_prop_t prop)
 *        {
 *            LV_ASSERT_NULL(obj)
 *            lv_style_selector_t selector = part | obj->state;
 *            lv_style_value_t value_act = { .ptr = NULL };
 *            lv_style_res_t found = get_selector_style_prop(obj, selector,
 *                                                             prop,
 *                                                             &value_act);
 *            if (found == LV_STYLE_RES_FOUND) return value_act;
 *            return lv_style_prop_get_default(prop);
 *        }
 *
 *  - Each of the eight trivial wrappers calls FUN_0044bdea with one
 *    literal LV_STYLE_* property id: 94, 98, 99, 120, 121, 105, 39, and
 *    117. Per third_party/lvgl/src/misc/lv_style.h those are exactly
 *    LV_STYLE_TEXT_ALIGN, LV_STYLE_OPA, LV_STYLE_OPA_LAYERED,
 *    LV_STYLE_RECOLOR, LV_STYLE_RECOLOR_OPA, LV_STYLE_BLEND_MODE,
 *    LV_STYLE_BASE_DIR, and LV_STYLE_BITMAP_MASK_SRC -- exactly the
 *    property ids used by the matching
 *    lv_obj_get_style_{text_align,opa,opa_layered,recolor,recolor_opa,
 *    blend_mode,base_dir,bitmap_mask_src}() `static inline` wrappers in
 *    third_party/lvgl/src/core/lv_obj_style_gen.h. Every wrapper but the
 *    color one truncates FUN_0044bdea's return to one byte before
 *    re-extending it for its own return (Ghidra decompiles the call
 *    result as `byte`), matching those generated wrappers' `uint8_t`-sized
 *    enum/opacity return casts; the color wrapper (recolor) instead
 *    forwards the full 32-bit result untouched, matching a 3-byte
 *    `lv_color_t` return. The stock IAR build chose not to inline any of
 *    these `static inline` functions -- like every other function in this
 *    retained cluster they are out-of-line, separately addressed
 *    functions; this port reproduces that topology directly instead of
 *    including the shared header (whose `static` linkage would make the
 *    port's own out-of-line copies unreachable from other translation
 *    units compiled against the same header).
 *
 * get_selector_style_prop() and lv_style_prop_get_default() are outside
 * this closure (see g2/docs/research/g2-lvgl-obj-style-prop.md and the
 * AM-011 g2/docs/progress.md entry); they are called at their
 * still-retained stock addresses, the same technique
 * runtime_obj_spec_attr.c already uses for the shared LV_ASSERT log
 * helper at 0x0044D25D.
 */

#include <stddef.h>
#include <stdint.h>

/* ---- lv_style.h / lv_obj_style.h / lv_types.h (LVGL 9.3) type slice ---- */

typedef uint32_t open_cfw_lvgl_part_t;       /* lv_part_t */
typedef uint8_t  open_cfw_lvgl_style_prop_t; /* lv_style_prop_t */

/* lv_color_t: third_party/lvgl/src/misc/lv_color.h, blue/green/red order. */
typedef struct {
    unsigned char blue;
    unsigned char green;
    unsigned char red;
} open_cfw_lvgl_color_t;

/* lv_style_value_t: third_party/lvgl/src/misc/lv_style.h. */
typedef union {
    int32_t num;
    const void *ptr;
    open_cfw_lvgl_color_t color;
} open_cfw_lvgl_style_value_t;

enum {
    OPEN_CFW_LV_STYLE_RES_NOT_FOUND = 0,
    OPEN_CFW_LV_STYLE_RES_FOUND = 1
};

/* third_party/lvgl/src/misc/lv_style.h property ids used by this closure. */
enum {
    OPEN_CFW_LV_STYLE_BASE_DIR = 39,
    OPEN_CFW_LV_STYLE_TEXT_ALIGN = 94,
    OPEN_CFW_LV_STYLE_OPA = 98,
    OPEN_CFW_LV_STYLE_OPA_LAYERED = 99,
    OPEN_CFW_LV_STYLE_BLEND_MODE = 105,
    OPEN_CFW_LV_STYLE_BITMAP_MASK_SRC = 117,
    OPEN_CFW_LV_STYLE_RECOLOR = 120,
    OPEN_CFW_LV_STYLE_RECOLOR_OPA = 121
};

/* Only field this closure touches: lv_obj_t.state at +0x28, evidenced by
 * FUN_0044bdea's `*(ushort *)(obj + 0x28)` read (see the header above). */
struct open_cfw_lvgl_obj_view {
    unsigned char reserved_00[0x28];
    unsigned short state;
};

_Static_assert(
    offsetof(struct open_cfw_lvgl_obj_view, state) == 0x28U,
    "lv_obj_t state offset changed"
);

#ifndef OPEN_CFW_LVGL_GET_SELECTOR_STYLE_PROP
typedef unsigned char (*open_cfw_lvgl_get_selector_style_prop_fn)(
    const struct open_cfw_lvgl_obj_view *obj,
    open_cfw_lvgl_part_t selector,
    open_cfw_lvgl_style_prop_t prop,
    open_cfw_lvgl_style_value_t *value
);
#define OPEN_CFW_LVGL_GET_SELECTOR_STYLE_PROP(obj, selector, prop, value) \
    (((open_cfw_lvgl_get_selector_style_prop_fn) \
        (__UINTPTR_TYPE__)0x0044CE8BU)((obj), (selector), (prop), (value)))
#endif

#ifndef OPEN_CFW_LVGL_STYLE_PROP_GET_DEFAULT
typedef open_cfw_lvgl_style_value_t (*open_cfw_lvgl_style_prop_get_default_fn)(
    open_cfw_lvgl_style_prop_t prop
);
#define OPEN_CFW_LVGL_STYLE_PROP_GET_DEFAULT(prop) \
    (((open_cfw_lvgl_style_prop_get_default_fn) \
        (__UINTPTR_TYPE__)0x0048297DU)((prop)))
#endif

/* Shared LV_ASSERT_MSG log helper at 0x0044D25D; level/file/line/function/
 * format/expression/message, matching runtime_obj_spec_attr.c's use of the
 * same address. Only severity (3) and line (332) are independently
 * evidenced for this call site (see the header above); file, function, and
 * expression strings are file/call-site specific and are left 0
 * (unresolved) rather than guessed. The format and "NULL pointer" message
 * strings are shared, file-independent literals used by every
 * LV_ASSERT_MSG/LV_ASSERT_NULL call in the vendored library, reused here
 * from runtime_obj_spec_attr.c's independently documented resolution.
 */
#ifndef OPEN_CFW_LVGL_ASSERT_NULL_OBJ
#define OPEN_CFW_LVGL_ASSERT_FORMAT 0x00761CB0U
#define OPEN_CFW_LVGL_ASSERT_NULL_MESSAGE 0x00787610U
#define OPEN_CFW_LVGL_ASSERT_NULL_OBJ_LINE 332U
#define OPEN_CFW_LVGL_ASSERT_NULL_OBJ() \
    (((void (*)( \
        unsigned int, unsigned int, unsigned int, unsigned int, \
        unsigned int, unsigned int, unsigned int \
    ))0x0044D25DU)( \
        3U, 0U, OPEN_CFW_LVGL_ASSERT_NULL_OBJ_LINE, 0U, \
        OPEN_CFW_LVGL_ASSERT_FORMAT, 0U, OPEN_CFW_LVGL_ASSERT_NULL_MESSAGE \
    ))
#endif

#ifndef OPEN_CFW_LVGL_FATAL
#define OPEN_CFW_LVGL_FATAL() \
    do { \
        for (;;) { \
            *(volatile unsigned int *)(__UINTPTR_TYPE__)0xFFFFFFFFU = 0U; \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
open_cfw_lvgl_style_value_t open_cfw_lvgl_obj_get_style_prop(
    const struct open_cfw_lvgl_obj_view *obj,
    open_cfw_lvgl_part_t part,
    open_cfw_lvgl_style_prop_t prop
)
{
    open_cfw_lvgl_style_value_t value_act;
    unsigned char found;

    if (obj == (const struct open_cfw_lvgl_obj_view *)0) {
        OPEN_CFW_LVGL_ASSERT_NULL_OBJ();
        OPEN_CFW_LVGL_FATAL();
    }

    value_act.ptr = (const void *)0;
    found = OPEN_CFW_LVGL_GET_SELECTOR_STYLE_PROP(
        obj, part | (open_cfw_lvgl_part_t)obj->state, prop, &value_act
    );
    if (found == OPEN_CFW_LV_STYLE_RES_FOUND) {
        return value_act;
    }
    return OPEN_CFW_LVGL_STYLE_PROP_GET_DEFAULT(prop);
}

__attribute__((used, noinline))
uint8_t open_cfw_lvgl_obj_get_style_text_align(
    const struct open_cfw_lvgl_obj_view *obj, open_cfw_lvgl_part_t part
)
{
    return (uint8_t)open_cfw_lvgl_obj_get_style_prop(
        obj, part, OPEN_CFW_LV_STYLE_TEXT_ALIGN
    ).num;
}

__attribute__((used, noinline))
uint8_t open_cfw_lvgl_obj_get_style_opa(
    const struct open_cfw_lvgl_obj_view *obj, open_cfw_lvgl_part_t part
)
{
    return (uint8_t)open_cfw_lvgl_obj_get_style_prop(
        obj, part, OPEN_CFW_LV_STYLE_OPA
    ).num;
}

__attribute__((used, noinline))
uint8_t open_cfw_lvgl_obj_get_style_opa_layered(
    const struct open_cfw_lvgl_obj_view *obj, open_cfw_lvgl_part_t part
)
{
    return (uint8_t)open_cfw_lvgl_obj_get_style_prop(
        obj, part, OPEN_CFW_LV_STYLE_OPA_LAYERED
    ).num;
}

__attribute__((used, noinline))
open_cfw_lvgl_color_t open_cfw_lvgl_obj_get_style_recolor(
    const struct open_cfw_lvgl_obj_view *obj, open_cfw_lvgl_part_t part
)
{
    return open_cfw_lvgl_obj_get_style_prop(
        obj, part, OPEN_CFW_LV_STYLE_RECOLOR
    ).color;
}

__attribute__((used, noinline))
uint8_t open_cfw_lvgl_obj_get_style_recolor_opa(
    const struct open_cfw_lvgl_obj_view *obj, open_cfw_lvgl_part_t part
)
{
    return (uint8_t)open_cfw_lvgl_obj_get_style_prop(
        obj, part, OPEN_CFW_LV_STYLE_RECOLOR_OPA
    ).num;
}

__attribute__((used, noinline))
uint8_t open_cfw_lvgl_obj_get_style_blend_mode(
    const struct open_cfw_lvgl_obj_view *obj, open_cfw_lvgl_part_t part
)
{
    return (uint8_t)open_cfw_lvgl_obj_get_style_prop(
        obj, part, OPEN_CFW_LV_STYLE_BLEND_MODE
    ).num;
}

__attribute__((used, noinline))
uint8_t open_cfw_lvgl_obj_get_style_base_dir(
    const struct open_cfw_lvgl_obj_view *obj, open_cfw_lvgl_part_t part
)
{
    return (uint8_t)open_cfw_lvgl_obj_get_style_prop(
        obj, part, OPEN_CFW_LV_STYLE_BASE_DIR
    ).num;
}

__attribute__((used, noinline))
const void *open_cfw_lvgl_obj_get_style_bitmap_mask_src(
    const struct open_cfw_lvgl_obj_view *obj, open_cfw_lvgl_part_t part
)
{
    return open_cfw_lvgl_obj_get_style_prop(
        obj, part, OPEN_CFW_LV_STYLE_BITMAP_MASK_SRC
    ).ptr;
}

#undef OPEN_CFW_LVGL_GET_SELECTOR_STYLE_PROP
#undef OPEN_CFW_LVGL_STYLE_PROP_GET_DEFAULT
#undef OPEN_CFW_LVGL_ASSERT_NULL_OBJ
#undef OPEN_CFW_LVGL_FATAL
