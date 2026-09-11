/*
 * SPDX-License-Identifier: MIT
 *
 * Reconstruction of eleven LVGL v9.3.0-dev `src/core/lv_obj_pos.c` geometry
 * and reposition functions retained verbatim (module-for-module, including
 * matching LV_ASSERT_OBJ line numbers and lv_align_t/lv_event_t constants)
 * in the official G2 Apollo-main image between 0x0043FD9E and 0x004403E6,
 * plus the immediately following lv_obj_move_to/lv_obj_move_children_by
 * pair at 0x00440246/0x0044035E.
 *
 * Identification method: every function below was matched against the
 * pinned upstream source (third_party/lvgl, LVGL commit
 * 344c7c318047b7348e1be8572a9fd4260c251cfa, see third_party/lvgl/PROVENANCE.json
 * and docs/research/lvgl-version-recovery-audit.md) by (a) the LV_ASSERT_OBJ
 * fault-path line number baked into the decompiled `if (obj == NULL)` crash
 * branch, (b) exact numeric matches of LV_SIZE_CONTENT (0x3fffffff),
 * LV_OBJ_FLAG_FLOATING (1<<18 = 0x40000), LV_EVENT_CHILD_CHANGED (42/0x2a),
 * LV_EVENT_GET_SELF_SIZE (52/0x34), LV_BASE_DIR_RTL (1), and the lv_align_t
 * ordinals (TOP_LEFT=1 .. CENTER=9), and (c) statement-for-statement control
 * flow equivalence against the vendored source.  See
 * docs/research/g2-lvgl-obj-pos-source-admission.md for the full per-function
 * evidence table.
 *
 * The functions below are re-expressed as reviewed C against this file's
 * own minimal, evidence-scoped view of the retained `lv_obj_t` layout
 * (parent pointer, spec_attr->children array, and the coords rectangle;
 * see the OPEN_CFW_LV_OBJ_*_OFFSET constants) rather than pasted decompiler
 * output.  Every other LVGL call they make (style/parent/scroll accessors,
 * lv_obj_get_coords, lv_area_copy/lv_area_get_width/height, lv_area_is_in,
 * lv_obj_send_event, lv_obj_has_flag, lv_obj_mark_layout_as_dirty,
 * lv_obj_scrollbar_invalidate, and the sibling lv_obj_invalidate) still
 * lands on the retained image at its current address; those remain
 * open_cfw_retained_lvgl_obj_pos_* provider stubs until their own closures
 * land (see followups in the admission audit).
 */

#include <stddef.h>
#include <stdint.h>

typedef struct open_cfw_lv_obj open_cfw_lv_obj;

typedef struct open_cfw_lv_area {
    int32_t x1;
    int32_t y1;
    int32_t x2;
    int32_t y2;
} open_cfw_lv_area;

/* Offsets recovered from decompilation; only the fields this file touches
 * are modeled, the rest of lv_obj_t stays opaque.  These assume the 4-byte
 * pointer width of the real Cortex-M55 target; a host test build (64-bit
 * pointers) predefines them via offsetof() against its own object model
 * before including this file, so the pointer-chasing logic below stays
 * identical between the reviewed target build and the host oracle. */
#ifndef OPEN_CFW_LV_OBJ_PARENT_OFFSET
#define OPEN_CFW_LV_OBJ_PARENT_OFFSET      0x04u
#endif
#ifndef OPEN_CFW_LV_OBJ_SPEC_ATTR_OFFSET
#define OPEN_CFW_LV_OBJ_SPEC_ATTR_OFFSET   0x08u
#endif
#ifndef OPEN_CFW_LV_OBJ_COORDS_OFFSET
#define OPEN_CFW_LV_OBJ_COORDS_OFFSET      0x14u
#endif

#define OPEN_CFW_LV_PART_MAIN               0x00000000u
#define OPEN_CFW_LV_OBJ_FLAG_FLOATING       0x00040000u
#define OPEN_CFW_LV_SIZE_CONTENT            0x3fffffff
#define OPEN_CFW_LV_BASE_DIR_RTL            1
#define OPEN_CFW_LV_EVENT_CHILD_CHANGED     42
#define OPEN_CFW_LV_EVENT_GET_SELF_SIZE     52

#define OPEN_CFW_LV_ALIGN_DEFAULT      0
#define OPEN_CFW_LV_ALIGN_TOP_LEFT     1
#define OPEN_CFW_LV_ALIGN_TOP_MID      2
#define OPEN_CFW_LV_ALIGN_TOP_RIGHT    3
#define OPEN_CFW_LV_ALIGN_BOTTOM_LEFT  4
#define OPEN_CFW_LV_ALIGN_BOTTOM_MID   5
#define OPEN_CFW_LV_ALIGN_BOTTOM_RIGHT 6
#define OPEN_CFW_LV_ALIGN_LEFT_MID     7
#define OPEN_CFW_LV_ALIGN_RIGHT_MID    8
#define OPEN_CFW_LV_ALIGN_CENTER       9

__attribute__((unused)) static inline open_cfw_lv_obj *
open_cfw_lv_obj_parent_field(const open_cfw_lv_obj *obj)
{
    return *(open_cfw_lv_obj * const *)((const uint8_t *)obj + OPEN_CFW_LV_OBJ_PARENT_OFFSET);
}

__attribute__((unused)) static inline open_cfw_lv_area *
open_cfw_lv_obj_coords_field(const open_cfw_lv_obj *obj)
{
    return (open_cfw_lv_area *)((const uint8_t *)obj + OPEN_CFW_LV_OBJ_COORDS_OFFSET);
}

__attribute__((unused)) static inline open_cfw_lv_obj *
open_cfw_lv_obj_child_field(const open_cfw_lv_obj *obj, uint32_t index)
{
    /* obj->spec_attr->children[index]; spec_attr's first field is the
     * children pointer array (verified against the retained
     * lv_obj_move_children_by loop body). */
    uint8_t *spec_attr = *(uint8_t **)((uint8_t *)obj + OPEN_CFW_LV_OBJ_SPEC_ATTR_OFFSET);
    void **children = *(void ***)spec_attr;
    return (open_cfw_lv_obj *)children[index];
}

/* Forward declarations of this file's own leaves so any one of them can be
 * compiled in isolation (see the *_ONLY selectors) while still referencing
 * a sibling leaf; the integration tool resolves such references either to
 * the sibling's own placed address or, when built with
 * OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL, to the definition below. */
int32_t open_cfw_lvgl_obj_pos_get_width(const open_cfw_lv_obj *obj);
int32_t open_cfw_lvgl_obj_pos_get_height(const open_cfw_lv_obj *obj);
int32_t open_cfw_lvgl_obj_pos_get_content_width(const open_cfw_lv_obj *obj);
int32_t open_cfw_lvgl_obj_pos_get_content_height(const open_cfw_lv_obj *obj);
void open_cfw_lvgl_obj_pos_get_content_coords(const open_cfw_lv_obj *obj, open_cfw_lv_area *area);
int32_t open_cfw_lvgl_obj_pos_get_self_width(open_cfw_lv_obj *obj);
int32_t open_cfw_lvgl_obj_pos_get_self_height(open_cfw_lv_obj *obj);
int open_cfw_lvgl_obj_pos_refresh_self_size(open_cfw_lv_obj *obj);
void open_cfw_lvgl_obj_pos_move_children_by(
    open_cfw_lv_obj *obj, int32_t x_diff, int32_t y_diff, int ignore_floating
);
void open_cfw_lvgl_obj_pos_move_to(open_cfw_lv_obj *obj, int32_t x, int32_t y);
void open_cfw_lvgl_obj_pos_refr_pos(open_cfw_lv_obj *obj);

/* Retained providers: still opaque bytes elsewhere in the image, called at
 * their current fixed addresses (see PROVIDERS in
 * tools/integrate_g2_lvgl_obj_pos_overlay.py). */
int32_t open_cfw_retained_lvgl_obj_pos_get_style_width(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_height(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_x(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_y(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_align(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_translate_x(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_translate_y(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_base_dir(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_space_left(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_space_right(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_space_top(const open_cfw_lv_obj *obj, uint32_t selector);
int32_t open_cfw_retained_lvgl_obj_pos_get_style_space_bottom(const open_cfw_lv_obj *obj, uint32_t selector);
int open_cfw_retained_lvgl_obj_pos_is_layout_positioned(const open_cfw_lv_obj *obj);
void open_cfw_retained_lvgl_obj_pos_mark_layout_as_dirty(open_cfw_lv_obj *obj);
void open_cfw_retained_lvgl_obj_pos_get_coords(const open_cfw_lv_obj *obj, open_cfw_lv_area *coords);
int open_cfw_retained_lvgl_obj_pos_has_flag(const open_cfw_lv_obj *obj, uint32_t flag);
open_cfw_lv_obj *open_cfw_retained_lvgl_obj_pos_get_parent(const open_cfw_lv_obj *obj);
uint32_t open_cfw_retained_lvgl_obj_pos_get_child_count(const open_cfw_lv_obj *obj);
int32_t open_cfw_retained_lvgl_obj_pos_get_scroll_x(const open_cfw_lv_obj *obj);
int32_t open_cfw_retained_lvgl_obj_pos_get_scroll_y(const open_cfw_lv_obj *obj);
int open_cfw_retained_lvgl_obj_pos_area_is_in(const open_cfw_lv_area *in_area, const open_cfw_lv_area *out_area, int32_t radius);
void open_cfw_retained_lvgl_obj_pos_scrollbar_invalidate(open_cfw_lv_obj *obj);
void open_cfw_retained_lvgl_obj_pos_area_copy(open_cfw_lv_area *dest, const open_cfw_lv_area *src);
int32_t open_cfw_retained_lvgl_obj_pos_area_get_width(const open_cfw_lv_area *area);
int32_t open_cfw_retained_lvgl_obj_pos_area_get_height(const open_cfw_lv_area *area);
void open_cfw_retained_lvgl_obj_pos_send_event(open_cfw_lv_obj *obj, uint32_t event_code, void *param);
void open_cfw_retained_lvgl_obj_pos_invalidate(const open_cfw_lv_obj *obj);

/* lv_log_add(), the retained sink LV_ASSERT_OBJ()/LV_ASSERT_NULL() reduce to
 * in this build's config (LV_USE_ASSERT_OBJ=0, LV_USE_ASSERT_NULL=1, see
 * third_party/lvgl/src/core/lv_obj.h and .../misc/lv_assert.h).  Variadic,
 * matching the retained image's own call sites. */
void open_cfw_retained_lvgl_obj_pos_log_add(
    int level, const char *file, int line, const char *func,
    const char *format, ...
);

/* LV_ASSERT_NULL(obj) as LV_ASSERT_OBJ(obj, MY_CLASS) resolves to in this
 * build (LV_USE_ASSERT_OBJ=0): log then LV_ASSERT_HANDLER (`while(1);` by
 * default, see lv_conf_internal.h).  `line` is the exact assert-site line
 * number recovered from this function's retained call in the official
 * image (see docs/research/g2-lvgl-obj-pos-source-admission.md); `func` is
 * the retained __func__ string, also recovered byte-for-byte from the
 * image's rodata. */
#define OPEN_CFW_LVGL_OBJ_POS_ASSERT_NULL(obj_ptr, line, func)               \
    do {                                                                     \
        if ((obj_ptr) == NULL) {                                             \
            open_cfw_retained_lvgl_obj_pos_log_add(                          \
                3, "third_party/lvgl/src/core/lv_obj_pos.c", (line), (func), \
                "Asserted at expression: %s (%s)", "obj != NULL",            \
                "NULL pointer"                                               \
            );                                                               \
            while (1) { }                                                    \
        }                                                                    \
    } while (0)

#if defined(OPEN_CFW_LVGL_OBJ_POS_GET_WIDTH_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_get_width() [lv_obj_pos.c:543-548]; LV_ASSERT_OBJ line and
 * __func__ recovered verbatim from the retained call at 0x0043fd9e. */
__attribute__((used, noinline))
int32_t open_cfw_lvgl_obj_pos_get_width(const open_cfw_lv_obj *obj)
{
    OPEN_CFW_LVGL_OBJ_POS_ASSERT_NULL(obj, 528, "lv_obj_get_width");
    return open_cfw_retained_lvgl_obj_pos_area_get_width(open_cfw_lv_obj_coords_field(obj));
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_GET_HEIGHT_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_get_height() [lv_obj_pos.c:550-555]; recovered from the
 * retained call at 0x0043fdda. */
__attribute__((used, noinline))
int32_t open_cfw_lvgl_obj_pos_get_height(const open_cfw_lv_obj *obj)
{
    OPEN_CFW_LVGL_OBJ_POS_ASSERT_NULL(obj, 545, "lv_obj_get_height");
    return open_cfw_retained_lvgl_obj_pos_area_get_height(open_cfw_lv_obj_coords_field(obj));
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_GET_CONTENT_WIDTH_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_get_content_width() [lv_obj_pos.c:557-565]; recovered from
 * the retained call at 0x0043fe16. */
__attribute__((used, noinline))
int32_t open_cfw_lvgl_obj_pos_get_content_width(const open_cfw_lv_obj *obj)
{
    int32_t left;
    int32_t right;
    OPEN_CFW_LVGL_OBJ_POS_ASSERT_NULL(obj, 559, "lv_obj_get_content_width");
    left = open_cfw_retained_lvgl_obj_pos_get_style_space_left(obj, OPEN_CFW_LV_PART_MAIN);
    right = open_cfw_retained_lvgl_obj_pos_get_style_space_right(obj, OPEN_CFW_LV_PART_MAIN);
    return (open_cfw_lvgl_obj_pos_get_width(obj) - left) - right;
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_GET_CONTENT_HEIGHT_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_get_content_height() [lv_obj_pos.c:567-575]; recovered
 * from the retained call at 0x0043fe70. */
__attribute__((used, noinline))
int32_t open_cfw_lvgl_obj_pos_get_content_height(const open_cfw_lv_obj *obj)
{
    int32_t top;
    int32_t bottom;
    OPEN_CFW_LVGL_OBJ_POS_ASSERT_NULL(obj, 569, "lv_obj_get_content_height");
    top = open_cfw_retained_lvgl_obj_pos_get_style_space_top(obj, OPEN_CFW_LV_PART_MAIN);
    bottom = open_cfw_retained_lvgl_obj_pos_get_style_space_bottom(obj, OPEN_CFW_LV_PART_MAIN);
    return (open_cfw_lvgl_obj_pos_get_height(obj) - top) - bottom;
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_GET_CONTENT_COORDS_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_get_content_coords() [lv_obj_pos.c:577-587]; recovered
 * from the retained call at 0x0043feca. */
__attribute__((used, noinline))
void open_cfw_lvgl_obj_pos_get_content_coords(const open_cfw_lv_obj *obj, open_cfw_lv_area *area)
{
    OPEN_CFW_LVGL_OBJ_POS_ASSERT_NULL(obj, 579, "lv_obj_get_content_coords");
    open_cfw_retained_lvgl_obj_pos_get_coords(obj, area);
    area->x1 += open_cfw_retained_lvgl_obj_pos_get_style_space_left(obj, OPEN_CFW_LV_PART_MAIN);
    area->x2 -= open_cfw_retained_lvgl_obj_pos_get_style_space_right(obj, OPEN_CFW_LV_PART_MAIN);
    area->y1 += open_cfw_retained_lvgl_obj_pos_get_style_space_top(obj, OPEN_CFW_LV_PART_MAIN);
    area->y2 -= open_cfw_retained_lvgl_obj_pos_get_style_space_bottom(obj, OPEN_CFW_LV_PART_MAIN);
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_GET_SELF_WIDTH_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_get_self_width() [lv_obj_pos.c:589-594]. */
__attribute__((used, noinline))
int32_t open_cfw_lvgl_obj_pos_get_self_width(open_cfw_lv_obj *obj)
{
    int32_t p[2];
    p[0] = 0;
    p[1] = -OPEN_CFW_LV_SIZE_CONTENT;
    open_cfw_retained_lvgl_obj_pos_send_event(obj, OPEN_CFW_LV_EVENT_GET_SELF_SIZE, p);
    return p[0];
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_GET_SELF_HEIGHT_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_get_self_height() [lv_obj_pos.c:596-601]. */
__attribute__((used, noinline))
int32_t open_cfw_lvgl_obj_pos_get_self_height(open_cfw_lv_obj *obj)
{
    int32_t p[2];
    p[0] = -OPEN_CFW_LV_SIZE_CONTENT;
    p[1] = 0;
    open_cfw_retained_lvgl_obj_pos_send_event(obj, OPEN_CFW_LV_EVENT_GET_SELF_SIZE, p);
    return p[1];
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_REFRESH_SELF_SIZE_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_refresh_self_size() [lv_obj_pos.c:603-611]. */
__attribute__((used, noinline))
int open_cfw_lvgl_obj_pos_refresh_self_size(open_cfw_lv_obj *obj)
{
    int32_t w_set = open_cfw_retained_lvgl_obj_pos_get_style_width(obj, OPEN_CFW_LV_PART_MAIN);
    int32_t h_set = open_cfw_retained_lvgl_obj_pos_get_style_height(obj, OPEN_CFW_LV_PART_MAIN);
    if (w_set != OPEN_CFW_LV_SIZE_CONTENT && h_set != OPEN_CFW_LV_SIZE_CONTENT) {
        return 0;
    }
    open_cfw_retained_lvgl_obj_pos_mark_layout_as_dirty(obj);
    return 1;
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_MOVE_CHILDREN_BY_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_move_children_by() [lv_obj_pos.c:765-779]. */
__attribute__((used, noinline))
void open_cfw_lvgl_obj_pos_move_children_by(
    open_cfw_lv_obj *obj, int32_t x_diff, int32_t y_diff, int ignore_floating
)
{
    uint32_t count = open_cfw_retained_lvgl_obj_pos_get_child_count(obj);
    uint32_t i;
    for (i = 0; i < count; ++i) {
        open_cfw_lv_obj *child = open_cfw_lv_obj_child_field(obj, i);
        if (ignore_floating &&
            open_cfw_retained_lvgl_obj_pos_has_flag(child, OPEN_CFW_LV_OBJ_FLAG_FLOATING)) {
            continue;
        }
        open_cfw_lv_area *coords = open_cfw_lv_obj_coords_field(child);
        coords->x1 += x_diff;
        coords->y1 += y_diff;
        coords->x2 += x_diff;
        coords->y2 += y_diff;
        open_cfw_lvgl_obj_pos_move_children_by(child, x_diff, y_diff, 0);
    }
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_MOVE_TO_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_move_to() [lv_obj_pos.c:696-763]. */
__attribute__((used, noinline))
void open_cfw_lvgl_obj_pos_move_to(open_cfw_lv_obj *obj, int32_t x, int32_t y)
{
    open_cfw_lv_obj *parent = open_cfw_lv_obj_parent_field(obj);
    open_cfw_lv_area *own_coords = open_cfw_lv_obj_coords_field(obj);
    int32_t diff_x;
    int32_t diff_y;
    open_cfw_lv_area ori;
    open_cfw_lv_area parent_fit_area;
    int on1 = 0;

    if (parent != NULL) {
        open_cfw_lv_area *parent_coords = open_cfw_lv_obj_coords_field(parent);
        if (open_cfw_retained_lvgl_obj_pos_has_flag(obj, OPEN_CFW_LV_OBJ_FLAG_FLOATING)) {
            x += parent_coords->x1;
            y += parent_coords->y1;
        } else {
            x += parent_coords->x1 - open_cfw_retained_lvgl_obj_pos_get_scroll_x(parent);
            y += parent_coords->y1 - open_cfw_retained_lvgl_obj_pos_get_scroll_y(parent);
        }
        x += open_cfw_retained_lvgl_obj_pos_get_style_space_left(parent, OPEN_CFW_LV_PART_MAIN);
        y += open_cfw_retained_lvgl_obj_pos_get_style_space_top(parent, OPEN_CFW_LV_PART_MAIN);
    }

    diff_x = x - own_coords->x1;
    diff_y = y - own_coords->y1;
    if (diff_x == 0 && diff_y == 0) {
        return;
    }

    open_cfw_retained_lvgl_obj_pos_invalidate(obj);
    open_cfw_retained_lvgl_obj_pos_get_coords(obj, &ori);

    if (parent != NULL) {
        open_cfw_lvgl_obj_pos_get_content_coords(parent, &parent_fit_area);
        on1 = open_cfw_retained_lvgl_obj_pos_area_is_in(&ori, &parent_fit_area, 0);
        if (!on1) {
            open_cfw_retained_lvgl_obj_pos_scrollbar_invalidate(parent);
        }
    }

    own_coords->x1 += diff_x;
    own_coords->y1 += diff_y;
    own_coords->x2 += diff_x;
    own_coords->y2 += diff_y;

    open_cfw_lvgl_obj_pos_move_children_by(obj, diff_x, diff_y, 0);

    if (parent != NULL) {
        open_cfw_retained_lvgl_obj_pos_send_event(parent, OPEN_CFW_LV_EVENT_CHILD_CHANGED, obj);
    }

    open_cfw_retained_lvgl_obj_pos_invalidate(obj);

    if (parent != NULL) {
        int on2 = open_cfw_retained_lvgl_obj_pos_area_is_in(own_coords, &parent_fit_area, 0);
        if (on1 || (!on1 && on2)) {
            open_cfw_retained_lvgl_obj_pos_scrollbar_invalidate(parent);
        }
    }
}
#endif

#if defined(OPEN_CFW_LVGL_OBJ_POS_REFR_POS_ONLY) || defined(OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL)
/* Matches lv_obj_refr_pos() [lv_obj_pos.c:613-694]. */
__attribute__((used, noinline))
void open_cfw_lvgl_obj_pos_refr_pos(open_cfw_lv_obj *obj)
{
    open_cfw_lv_obj *parent;
    int32_t x;
    int32_t y;
    int32_t pw;
    int32_t ph;
    int32_t tr_x;
    int32_t tr_y;
    int32_t w;
    int32_t h;
    int32_t align;

    if (open_cfw_retained_lvgl_obj_pos_is_layout_positioned(obj)) {
        return;
    }

    parent = open_cfw_retained_lvgl_obj_pos_get_parent(obj);
    x = open_cfw_retained_lvgl_obj_pos_get_style_x(obj, OPEN_CFW_LV_PART_MAIN);
    y = open_cfw_retained_lvgl_obj_pos_get_style_y(obj, OPEN_CFW_LV_PART_MAIN);

    if (parent == NULL) {
        open_cfw_lvgl_obj_pos_move_to(obj, x, y);
        return;
    }

    pw = open_cfw_lvgl_obj_pos_get_content_width(parent);
    ph = open_cfw_lvgl_obj_pos_get_content_height(parent);

    /* Percentage x/y: LV_COORD_IS_PCT() true and not LV_SIZE_CONTENT was
     * already excluded by the direct-value style getters above returning a
     * plain pixel value for the common case; the retained percentage path
     * (LV_COORD_TYPE_SPEC, plain value < LV_COORD_MAX) is preserved here. */
    if (((uint32_t)x & 0x60000000u) == 0x20000000u && ((int32_t)((uint32_t)x & 0x9fffffffu)) < 0x1fffffff) {
        if (open_cfw_retained_lvgl_obj_pos_get_style_width(parent, OPEN_CFW_LV_PART_MAIN) == OPEN_CFW_LV_SIZE_CONTENT) {
            x = 0;
        } else {
            uint32_t plain = (uint32_t)x & 0x9fffffffu;
            int32_t pct = ((int32_t)plain < 0x10000000) ? (int32_t)plain : (int32_t)(0xfffffff - plain);
            x = (int32_t)(((int64_t)pw * pct) / 100);
        }
    }
    if (((uint32_t)y & 0x60000000u) == 0x20000000u && ((int32_t)((uint32_t)y & 0x9fffffffu)) < 0x1fffffff) {
        if (open_cfw_retained_lvgl_obj_pos_get_style_height(parent, OPEN_CFW_LV_PART_MAIN) == OPEN_CFW_LV_SIZE_CONTENT) {
            y = 0;
        }
        {
            uint32_t plain = (uint32_t)y & 0x9fffffffu;
            int32_t pct = ((int32_t)plain < 0x10000000) ? (int32_t)plain : (int32_t)(0xfffffff - plain);
            y = (int32_t)(((int64_t)ph * pct) / 100);
        }
    }

    tr_x = open_cfw_retained_lvgl_obj_pos_get_style_translate_x(obj, OPEN_CFW_LV_PART_MAIN);
    tr_y = open_cfw_retained_lvgl_obj_pos_get_style_translate_y(obj, OPEN_CFW_LV_PART_MAIN);
    w = open_cfw_lvgl_obj_pos_get_width(obj);
    h = open_cfw_lvgl_obj_pos_get_height(obj);
    if (((uint32_t)tr_x & 0x60000000u) == 0x20000000u && ((int32_t)((uint32_t)tr_x & 0x9fffffffu)) < 0x1fffffff) {
        uint32_t plain = (uint32_t)tr_x & 0x9fffffffu;
        int32_t pct = ((int32_t)plain < 0x10000000) ? (int32_t)plain : (int32_t)(0xfffffff - plain);
        tr_x = (int32_t)(((int64_t)w * pct) / 100);
    }
    if (((uint32_t)tr_y & 0x60000000u) == 0x20000000u && ((int32_t)((uint32_t)tr_y & 0x9fffffffu)) < 0x1fffffff) {
        uint32_t plain = (uint32_t)tr_y & 0x9fffffffu;
        int32_t pct = ((int32_t)plain < 0x10000000) ? (int32_t)plain : (int32_t)(0xfffffff - plain);
        tr_y = (int32_t)(((int64_t)h * pct) / 100);
    }
    x += tr_x;
    y += tr_y;

    align = open_cfw_retained_lvgl_obj_pos_get_style_align(obj, OPEN_CFW_LV_PART_MAIN);
    if (align == OPEN_CFW_LV_ALIGN_DEFAULT) {
        align = (open_cfw_retained_lvgl_obj_pos_get_style_base_dir(parent, OPEN_CFW_LV_PART_MAIN) ==
                 OPEN_CFW_LV_BASE_DIR_RTL)
                    ? OPEN_CFW_LV_ALIGN_TOP_RIGHT
                    : OPEN_CFW_LV_ALIGN_TOP_LEFT;
    }

    switch (align) {
        case OPEN_CFW_LV_ALIGN_TOP_LEFT:
            break;
        case OPEN_CFW_LV_ALIGN_TOP_MID:
            x += pw / 2 - w / 2;
            break;
        case OPEN_CFW_LV_ALIGN_TOP_RIGHT:
            x += pw - w;
            break;
        case OPEN_CFW_LV_ALIGN_LEFT_MID:
            y += ph / 2 - h / 2;
            break;
        case OPEN_CFW_LV_ALIGN_BOTTOM_LEFT:
            y += ph - h;
            break;
        case OPEN_CFW_LV_ALIGN_BOTTOM_MID:
            x += pw / 2 - w / 2;
            y += ph - h;
            break;
        case OPEN_CFW_LV_ALIGN_BOTTOM_RIGHT:
            x += pw - w;
            y += ph - h;
            break;
        case OPEN_CFW_LV_ALIGN_RIGHT_MID:
            x += pw - w;
            y += ph / 2 - h / 2;
            break;
        case OPEN_CFW_LV_ALIGN_CENTER:
            x += pw / 2 - w / 2;
            y += ph / 2 - h / 2;
            break;
        default:
            break;
    }

    open_cfw_lvgl_obj_pos_move_to(obj, x, y);
}
#endif
