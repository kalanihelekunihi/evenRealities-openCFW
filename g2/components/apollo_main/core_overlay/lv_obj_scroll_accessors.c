/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of nine LVGL 9.3-dev `lv_obj_scroll.c` scroll
 * getters/setter closing the stock G2 2.2.6.10 Apollo-main span
 * 0x0044E412..0x0044E79E (plus 0x0044E75E's `lv_obj_get_scroll_end`).
 *
 * Every function body below is a line-for-line translation of the
 * authenticated vendored snapshot at
 * `third_party/lvgl/src/core/lv_obj_scroll.c` (openCFW compatibility-ceiling
 * commit 344c7c318047b7348e1be8572a9fd4260c251cfa; see
 * `third_party/lvgl/README.openCFW.md`), not of the Ghidra decompilation.
 * The decompilation is used only to identify which upstream function each
 * stock entry point is and to confirm the field layout below.
 *
 * `lv_obj_spec_attr_t` field offsets are derived, not assumed: G2's
 * recovered configuration does not pin `LV_DRAW_TRANSFORM_USE_MATRIX` or
 * `LV_USE_OBJ_NAME` (see `third_party/lvgl/g2-config/lv_conf_recovered.h`).
 * With both features disabled, `struct _lv_obj_spec_attr_t` in
 * `third_party/lvgl/src/core/lv_obj_private.h` places `scroll` (an
 * `lv_point_t`, i.e. two `int32_t`) at byte offset 0x20 and the
 * `scrollbar_mode`/`scroll_snap_x`/`scroll_snap_y`/`scroll_dir` bitfield
 * half-word at byte offset 0x32:
 *
 *   children (ptr, 4) + group_p (ptr, 4)
 *     + event_list (lv_array_t 20B + 1B flags, padded to 24B)
 *     = 32 (0x20) bytes before `scroll`;
 *   scroll.x @0x20, scroll.y @0x24 (8 bytes);
 *   ext_click_pad @0x28, ext_draw_size @0x2C (8 bytes);
 *   child_cnt (uint16_t) @0x30;
 *   bitfield half-word @0x32: scrollbar_mode[1:0], scroll_snap_x[3:2],
 *   scroll_snap_y[5:4], scroll_dir[9:6], layer_type[11:10], name_static[12].
 *
 * That derived layout matches every offset (0x20, 0x24, 0x32) and every bit
 * position/mask/shift/default value read by the eight decompiled stock
 * bodies at 0x0044E412..0x0044E4AA, which is why this file admits them as
 * this exact upstream source rather than a byte-array trap or a typed
 * external-provider stub. `open_cfw_lv_obj_allocate_spec_attr` (stock
 * 0x0043E1FA) and `open_cfw_lv_anim_get` (stock 0x00450566) remain outside
 * this closure's byte range and are called through their retained stock
 * entries, matching the existing `lv_display_setup.c` convention for
 * cross-boundary calls into not-yet-closed retained code.
 */

#include <stddef.h>
#include <stdint.h>

/* Minimal G2 `lv_obj_t` view: only the fields this cluster reads. */
typedef struct {
    const void *class_p;
    void *parent;
    void *spec_attr;
} open_cfw_lv_obj_view_t;

_Static_assert(offsetof(open_cfw_lv_obj_view_t, spec_attr) == 0x08U,
    "G2 lv_obj_t spec_attr offset changed");

/* Minimal G2 `lv_obj_spec_attr_t` view: only the fields this cluster reads.
 * `reserved_*` spans are never dereferenced; they exist solely to place the
 * named fields at their derived offsets. */
typedef struct {
    unsigned char reserved_children_group_events[0x20];
    int32_t scroll_x;
    int32_t scroll_y;
    unsigned char reserved_click_draw_child_count[0x0A];
    uint16_t flags;
} open_cfw_lv_obj_spec_attr_view_t;

_Static_assert(offsetof(open_cfw_lv_obj_spec_attr_view_t, scroll_x) == 0x20U,
    "G2 lv_obj_spec_attr_t scroll.x offset changed");
_Static_assert(offsetof(open_cfw_lv_obj_spec_attr_view_t, scroll_y) == 0x24U,
    "G2 lv_obj_spec_attr_t scroll.y offset changed");
_Static_assert(offsetof(open_cfw_lv_obj_spec_attr_view_t, flags) == 0x32U,
    "G2 lv_obj_spec_attr_t scrollbar/scroll_dir bitfield offset changed");

#define OPEN_CFW_LV_OBJ_SCROLLBAR_MODE_MASK 0x0003U
#define OPEN_CFW_LV_OBJ_SCROLL_SNAP_X_SHIFT 2U
#define OPEN_CFW_LV_OBJ_SCROLL_SNAP_X_MASK 0x0003U
#define OPEN_CFW_LV_OBJ_SCROLL_SNAP_Y_SHIFT 4U
#define OPEN_CFW_LV_OBJ_SCROLL_SNAP_Y_MASK 0x0003U
#define OPEN_CFW_LV_OBJ_SCROLL_DIR_SHIFT 6U
#define OPEN_CFW_LV_OBJ_SCROLL_DIR_MASK 0x000FU

/* `lv_scrollbar_mode_t` / `lv_scroll_snap_t` / `lv_dir_t` defaults, from
 * `third_party/lvgl/src/core/lv_obj_scroll.h` and
 * `third_party/lvgl/src/misc/lv_area.h`. */
#define OPEN_CFW_LV_SCROLLBAR_MODE_AUTO 3U
#define OPEN_CFW_LV_SCROLL_SNAP_NONE 0U
#define OPEN_CFW_LV_DIR_ALL 0x0FU

/* `lv_obj_allocate_spec_attr(lv_obj_t *)`, stock entry 0x0043E1FA. Ensures
 * `obj->spec_attr` is non-NULL, allocating and zero-initializing it on first
 * use. Outside this closure's byte range; called through its retained stock
 * entry (odd/thumb address per AAPCS), as `lv_display_setup.c` already does
 * for other not-yet-closed cross-boundary calls. */
typedef void (*open_cfw_lv_obj_allocate_spec_attr_fn)(open_cfw_lv_obj_view_t *obj);

#ifndef OPEN_CFW_LV_OBJ_ALLOCATE_SPEC_ATTR
#define OPEN_CFW_LV_OBJ_ALLOCATE_SPEC_ATTR(obj) \
    (((open_cfw_lv_obj_allocate_spec_attr_fn)0x0043E1FBU)(obj))
#endif

/* `lv_anim_t *lv_anim_get(void *var, lv_anim_exec_xcb_t exec_cb)`, stock
 * entry 0x00450566. Outside this closure's byte range; called through its
 * retained stock entry for the same reason as above. */
typedef void *(*open_cfw_lv_anim_get_fn)(const open_cfw_lv_obj_view_t *var, const void *exec_cb);

#ifndef OPEN_CFW_LV_ANIM_GET
#define OPEN_CFW_LV_ANIM_GET(var, exec_cb) \
    (((open_cfw_lv_anim_get_fn)0x00450567U)((var), (exec_cb)))
#endif

/* Stock `scroll_x_anim`/`scroll_y_anim` static callback identities, read
 * verbatim from the authenticated image literal pool at 0x0044EB1C and
 * 0x0044EB20 (already odd/thumb-tagged in the stored word, matching how the
 * original compiler emitted `&scroll_x_anim`/`&scroll_y_anim`). They are
 * never called here -- only compared by `lv_anim_get`'s internal search --
 * so no additional closure is required to reference them. */
#ifndef OPEN_CFW_LV_OBJ_SCROLL_X_ANIM_CB
#define OPEN_CFW_LV_OBJ_SCROLL_X_ANIM_CB ((const void *)0x0044F3B9U)
#endif
#ifndef OPEN_CFW_LV_OBJ_SCROLL_Y_ANIM_CB
#define OPEN_CFW_LV_OBJ_SCROLL_Y_ANIM_CB ((const void *)0x0044F3D5U)
#endif

/* `lv_anim_t.end_value` field offset, read verbatim from the decompiled
 * stock `lv_obj_get_scroll_end` body (`0x0044E75E`); `lv_anim_t` itself
 * remains outside this closure. */
#define OPEN_CFW_LV_ANIM_END_VALUE_OFFSET 0x2CU

/*
 * lv_obj_get_scroll_x(const lv_obj_t *obj) -- stock 0x0044E486.
 *
 *   int32_t lv_obj_get_scroll_x(const lv_obj_t * obj)
 *   {
 *       if(obj->spec_attr == NULL) return 0;
 *       return -obj->spec_attr->scroll.x;
 *   }
 */
__attribute__((used, noinline))
int32_t open_cfw_lv_obj_get_scroll_x(const open_cfw_lv_obj_view_t *obj)
{
    const open_cfw_lv_obj_spec_attr_view_t *spec_attr = obj->spec_attr;

    if (spec_attr == NULL) {
        return 0;
    }
    return -spec_attr->scroll_x;
}

/*
 * lv_obj_get_scroll_y(const lv_obj_t *obj) -- stock 0x0044E498.
 *
 *   int32_t lv_obj_get_scroll_y(const lv_obj_t * obj)
 *   {
 *       if(obj->spec_attr == NULL) return 0;
 *       return -obj->spec_attr->scroll.y;
 *   }
 */
__attribute__((used, noinline))
int32_t open_cfw_lv_obj_get_scroll_y(const open_cfw_lv_obj_view_t *obj)
{
    const open_cfw_lv_obj_spec_attr_view_t *spec_attr = obj->spec_attr;

    if (spec_attr == NULL) {
        return 0;
    }
    return -spec_attr->scroll_y;
}

/*
 * lv_obj_get_scroll_top(const lv_obj_t *obj) -- stock 0x0044E4AA.
 *
 * Upstream defines this with the exact same body as `lv_obj_get_scroll_y`
 * (see `third_party/lvgl/src/core/lv_obj_scroll.c` lines 124-134); the two
 * stock bodies are independently confirmed byte-identical
 * (`sha256=63a361e...`), which is why the source below is a duplicate
 * function rather than one calling the other:
 *
 *   int32_t lv_obj_get_scroll_top(const lv_obj_t * obj)
 *   {
 *       if(obj->spec_attr == NULL) return 0;
 *       return -obj->spec_attr->scroll.y;
 *   }
 */
__attribute__((used, noinline))
int32_t open_cfw_lv_obj_get_scroll_top(const open_cfw_lv_obj_view_t *obj)
{
    const open_cfw_lv_obj_spec_attr_view_t *spec_attr = obj->spec_attr;

    if (spec_attr == NULL) {
        return 0;
    }
    return -spec_attr->scroll_y;
}

/*
 * lv_obj_get_scrollbar_mode(const lv_obj_t *obj) -- stock 0x0044E42C.
 *
 *   lv_scrollbar_mode_t lv_obj_get_scrollbar_mode(const lv_obj_t * obj)
 *   {
 *       if(obj->spec_attr) return (lv_scrollbar_mode_t) obj->spec_attr->scrollbar_mode;
 *       else return LV_SCROLLBAR_MODE_AUTO;
 *   }
 */
__attribute__((used, noinline))
uint8_t open_cfw_lv_obj_get_scrollbar_mode(const open_cfw_lv_obj_view_t *obj)
{
    const open_cfw_lv_obj_spec_attr_view_t *spec_attr = obj->spec_attr;

    if (spec_attr == NULL) {
        return (uint8_t)OPEN_CFW_LV_SCROLLBAR_MODE_AUTO;
    }
    return (uint8_t)(spec_attr->flags & OPEN_CFW_LV_OBJ_SCROLLBAR_MODE_MASK);
}

/*
 * lv_obj_get_scroll_dir(const lv_obj_t *obj) -- stock 0x0044E442.
 *
 *   lv_dir_t lv_obj_get_scroll_dir(const lv_obj_t * obj)
 *   {
 *       if(obj->spec_attr) return (lv_dir_t) obj->spec_attr->scroll_dir;
 *       else return LV_DIR_ALL;
 *   }
 */
__attribute__((used, noinline))
uint16_t open_cfw_lv_obj_get_scroll_dir(const open_cfw_lv_obj_view_t *obj)
{
    const open_cfw_lv_obj_spec_attr_view_t *spec_attr = obj->spec_attr;

    if (spec_attr == NULL) {
        return (uint16_t)OPEN_CFW_LV_DIR_ALL;
    }
    return (uint16_t)((spec_attr->flags >> OPEN_CFW_LV_OBJ_SCROLL_DIR_SHIFT)
        & OPEN_CFW_LV_OBJ_SCROLL_DIR_MASK);
}

/*
 * lv_obj_get_scroll_snap_x(const lv_obj_t *obj) -- stock 0x0044E45A.
 *
 *   lv_scroll_snap_t lv_obj_get_scroll_snap_x(const lv_obj_t * obj)
 *   {
 *       if(obj->spec_attr) return (lv_scroll_snap_t) obj->spec_attr->scroll_snap_x;
 *       else return LV_SCROLL_SNAP_NONE;
 *   }
 */
__attribute__((used, noinline))
uint8_t open_cfw_lv_obj_get_scroll_snap_x(const open_cfw_lv_obj_view_t *obj)
{
    const open_cfw_lv_obj_spec_attr_view_t *spec_attr = obj->spec_attr;

    if (spec_attr == NULL) {
        return (uint8_t)OPEN_CFW_LV_SCROLL_SNAP_NONE;
    }
    return (uint8_t)((spec_attr->flags >> OPEN_CFW_LV_OBJ_SCROLL_SNAP_X_SHIFT)
        & OPEN_CFW_LV_OBJ_SCROLL_SNAP_X_MASK);
}

/*
 * lv_obj_get_scroll_snap_y(const lv_obj_t *obj) -- stock 0x0044E470.
 *
 *   lv_scroll_snap_t lv_obj_get_scroll_snap_y(const lv_obj_t * obj)
 *   {
 *       if(obj->spec_attr) return (lv_scroll_snap_t) obj->spec_attr->scroll_snap_y;
 *       else return LV_SCROLL_SNAP_NONE;
 *   }
 */
__attribute__((used, noinline))
uint8_t open_cfw_lv_obj_get_scroll_snap_y(const open_cfw_lv_obj_view_t *obj)
{
    const open_cfw_lv_obj_spec_attr_view_t *spec_attr = obj->spec_attr;

    if (spec_attr == NULL) {
        return (uint8_t)OPEN_CFW_LV_SCROLL_SNAP_NONE;
    }
    return (uint8_t)((spec_attr->flags >> OPEN_CFW_LV_OBJ_SCROLL_SNAP_Y_SHIFT)
        & OPEN_CFW_LV_OBJ_SCROLL_SNAP_Y_MASK);
}

/*
 * lv_obj_set_scroll_snap_y(lv_obj_t *obj, lv_scroll_snap_t align) -- stock
 * 0x0044E412.
 *
 *   void lv_obj_set_scroll_snap_y(lv_obj_t * obj, lv_scroll_snap_t align)
 *   {
 *       lv_obj_allocate_spec_attr(obj);
 *       obj->spec_attr->scroll_snap_y = align;
 *   }
 */
__attribute__((used, noinline))
void open_cfw_lv_obj_set_scroll_snap_y(open_cfw_lv_obj_view_t *obj, uint8_t align)
{
    open_cfw_lv_obj_spec_attr_view_t *spec_attr;

    OPEN_CFW_LV_OBJ_ALLOCATE_SPEC_ATTR(obj);
    spec_attr = obj->spec_attr;
    spec_attr->flags = (uint16_t)(
        (spec_attr->flags
            & (uint16_t)~(OPEN_CFW_LV_OBJ_SCROLL_SNAP_Y_MASK << OPEN_CFW_LV_OBJ_SCROLL_SNAP_Y_SHIFT))
        | (uint16_t)((align & OPEN_CFW_LV_OBJ_SCROLL_SNAP_Y_MASK) << OPEN_CFW_LV_OBJ_SCROLL_SNAP_Y_SHIFT));
}

/*
 * lv_obj_get_scroll_end(lv_obj_t *obj, lv_point_t *end) -- stock 0x0044E75E.
 *
 *   void lv_obj_get_scroll_end(lv_obj_t * obj, lv_point_t * end)
 *   {
 *       lv_anim_t * a;
 *       a = lv_anim_get(obj, scroll_x_anim);
 *       end->x = a ? -a->end_value : lv_obj_get_scroll_x(obj);
 *
 *       a = lv_anim_get(obj, scroll_y_anim);
 *       end->y = a ? -a->end_value : lv_obj_get_scroll_y(obj);
 *   }
 */
__attribute__((used, noinline))
void open_cfw_lv_obj_get_scroll_end(open_cfw_lv_obj_view_t *obj, int32_t *end)
{
    const unsigned char *anim;

    anim = (const unsigned char *)OPEN_CFW_LV_ANIM_GET(obj, OPEN_CFW_LV_OBJ_SCROLL_X_ANIM_CB);
    end[0] = (anim != NULL)
        ? -*(const int32_t *)(anim + OPEN_CFW_LV_ANIM_END_VALUE_OFFSET)
        : open_cfw_lv_obj_get_scroll_x(obj);

    anim = (const unsigned char *)OPEN_CFW_LV_ANIM_GET(obj, OPEN_CFW_LV_OBJ_SCROLL_Y_ANIM_CB);
    end[1] = (anim != NULL)
        ? -*(const int32_t *)(anim + OPEN_CFW_LV_ANIM_END_VALUE_OFFSET)
        : open_cfw_lv_obj_get_scroll_y(obj);
}
