/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of the LVGL flex/grid layout helper cluster
 * retained in G2 firmware 2.2.6.10 at 0x0048C7B4..0x0048C920,
 * 0x0048C920..0x0048D3A0 (with the 0x0048D3A0..0x0048D3C8 literal pool
 * excluded), 0x0048D3C8..0x0048D4D0, and 0x0048D4D0..0x0048D4E6
 * (Apollo main
 * application, component `apollo_main`, work item AM-040): twenty-eight
 * functions, 3,074 bytes.
 *
 * Upstream: g2/third_party/lvgl (LVGL 9.3-dev commit
 * 344c7c318047b7348e1be8572a9fd4260c251cfa, see
 * g2/third_party/lvgl/PROVENANCE.json; the stock image's own rodata
 * names the vendor file
 * `D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\layouts\grid\lv_grid.c`):
 *  - `src/layouts/flex/lv_flex.c`: `lv_obj_get_width_with_margin`,
 *    `lv_obj_get_height_with_margin` (file-static; the stock IAR build
 *    emitted them out-of-line at 0x0048C7B4/0x0048C7D8).
 *  - `src/core/lv_obj_style.h`: `lv_obj_get_style_space_left`,
 *    `lv_obj_get_style_space_top` (static inline; out-of-line at
 *    0x0048C920/0x0048C94E). The stock bit tests (`lsls`+`bpl`)
 *    check LV_BORDER_SIDE_LEFT (0x04) and LV_BORDER_SIDE_TOP (0x02)
 *    exactly as the upstream ternary does.
 *  - `src/layouts/grid/lv_grid.c`: the ten `get_*` one-argument wrappers
 *    (each forwards to a grid style getter with part 0), `get_margin_hor`,
 *    `get_margin_ver`, `lv_div_round_closest`, `calc`, `calc_free`,
 *    `grid_update`, `lv_grid_init`, `calc_cols`, `calc_rows`,
 *    `item_repos`, and `grid_align`.
 *  - `src/misc/lv_area.h`: `lv_area_copy` (inline; out-of-line at
 *    0x0048C7FC; the stock word-copy order matches the upstream
 *    field-copy order).
 *  - `src/stdlib/lv_string.h`: `lv_memzero` (inline over `lv_memset`;
 *    out-of-line at 0x0048C80E calling the global `lv_memset` at
 *    0x00454746, which reorders `(dst, value, len)` onto the
 *    `__aeabi_memset`-shaped core at 0x0043C0E4).
 *  - `count_tracks` at 0x0048D4D0 is `lv_grid.c`'s file-static track
 *    counter (loop until LV_GRID_TEMPLATE_LAST == 0x1FFFFFFF).
 *
 * Identity evidence per function (see the audit
 * docs/research/lvgl-grid-engine-closure.md for the full table):
 *  - 0x0048C7B4/0x0048C7D8: three-term sums
 *    margin_left+width+margin_right / margin_top+height+margin_bottom,
 *    the exact bodies of the two `*_with_margin` flex statics.
 *  - 0x0048C920/0x0048C94E: pad_{left,top} plus border width gated on
 *    the matching border-side bit; callees are the property-0x12/0x30/
 *    0x34 and 0x10/0x30/0x34 getters recovered in
 *    lvgl_layout_style_getters.c.
 *  - 0x0048C97C..0x0048C9D6: single forwards with part 0 to the grid
 *    style getters (properties 0x7F..0x88), matching the ten `get_*`
 *    grid statics one for one (dsc arrays, positions, spans, aligns).
 *  - 0x0048C9E0/0x0048C9FC: margin_left+margin_right /
 *    margin_top+margin_bottom, the `get_margin_hor`/`get_margin_ver`
 *    bodies. 0x0048CA18: `(divisor/2 + dividend)/divisor` via `sdiv`,
 *    the `lv_div_round_closest` body.
 *  - 0x0048CA26 stores the next function's entry with the Thumb bit
 *    (0x48CA3D) plus a NULL word through the layout-registry slot;
 *    upstream this is `lv_grid_init` registering `grid_update`.
 *  - 0x0048CA3C is `grid_update`: `calc` call, 16-byte hint memzero,
 *    space_left/top, scroll_x/y-corrected grid origin at hint+8/+12,
 *    per-child `item_repos` loop over spec_attr children/count,
 *    `calc_free`, LV_SIZE_CONTENT-gated `lv_obj_refr_size`, and the
 *    LV_EVENT_LAYOUT_CHANGED (0x33) send. The 0x3FFFFFFF compare is
 *    materialized in stock as `mvns r1, #0xC0000000`.
 *  - 0x0048CAD8 is `calc`: empty (no child 0) memzero of the 32-byte
 *    calc struct, else calc_rows/calc_cols, pad_column/pad_row gaps,
 *    RTL check on base_dir, CONTENT-gated auto flags from the
 *    w_layout (bit 11) / h_layout (bit 10) halfword at obj+0x2A --
 *    matching the upstream `_lv_obj_t` bitfield order -- and two
 *    `grid_align` calls filling grid_w/grid_h.
 *  - 0x0048CBDA is `calc_free`: four `lv_free` calls over the x/y/w/h
 *    slots, in order.
 *
 * Field offsets used below (obj+0x14 coords, obj+0x08 spec_attr,
 * spec_attr+0x00 children / +0x20 scroll.x / +0x24 scroll.y /
 * +0x30 child_cnt) agree with the retained `lv_obj_t` layout modeled
 * in lvgl_obj_pos.c and with third_party/lvgl/src/core/lv_obj_private.h
 * under the G2 configuration (no style cache, no object id).
 *
 * Callees outside this file stay at their retained stock addresses
 * (same technique as lvgl_obj_style_prop.c): the LVGL object core
 * (`lv_obj_get_width/height`, content sizes, scroll, child access,
 * parent, flags, invalidate, area get/set, event send, child move,
 * `lv_malloc/free/memcpy/memset`, `lv_log_add` WARN) at 0x0043E11C,
 * 0x0043FD9E, 0x0043FDDA, 0x0043FE16, 0x0043FE70, 0x0044035E,
 * 0x00440656, 0x0044D25C, 0x0044DCA2, 0x0044DCE2, 0x0044DDEA,
 * 0x0044E486, 0x0044E498, 0x0043F1A4 (refr), 0x0044F718,
 * 0x0044F758, 0x00450B6C, 0x00450B76, 0x00451598, 0x004515A4,
 * 0x00451670, 0x00454738, 0x00454746. The style getters live in
 * lvgl_layout_style_getters.c (same tranche).
 */

#include <stddef.h>
#include <stdint.h>

typedef struct open_cfw_lvgl_grid_area {
    int32_t x1;
    int32_t y1;
    int32_t x2;
    int32_t y2;
} open_cfw_lvgl_grid_area_t;

/* Upstream `item_repos_hint_t`: two scratch words, then the grid origin. */
typedef struct open_cfw_lvgl_grid_hint {
    uint32_t col;
    uint32_t row;
    int32_t grid_abs_x;
    int32_t grid_abs_y;
} open_cfw_lvgl_grid_hint_t;

/* Upstream `lv_grid_calc_t` (32 bytes under 32-bit pointers, matching the
 * 0x20-byte memzero the stock `calc` emits for the empty-container path). */
typedef struct open_cfw_lvgl_grid_calc {
    void *x;
    void *y;
    void *w;
    void *h;
    uint32_t col_num;
    uint32_t row_num;
    int32_t grid_w;
    int32_t grid_h;
} open_cfw_lvgl_grid_calc_t;

enum {
    OPEN_CFW_LVGL_PART_MAIN = 0U,
    OPEN_CFW_LVGL_SIZE_CONTENT = 0x3FFFFFFFU,
    OPEN_CFW_LVGL_GRID_TEMPLATE_LAST = 0x1FFFFFFFU,
    OPEN_CFW_LVGL_BASE_DIR_RTL = 1U,
    OPEN_CFW_LVGL_BORDER_SIDE_LEFT = 0x04U,
    OPEN_CFW_LVGL_BORDER_SIDE_TOP = 0x02U,
    OPEN_CFW_LVGL_EVENT_LAYOUT_CHANGED = 0x33U,
    OPEN_CFW_LVGL_OBJ_COORDS_OFFSET = 0x14U,
    OPEN_CFW_LVGL_OBJ_SPEC_ATTR_OFFSET = 0x08U,
    OPEN_CFW_LVGL_SPEC_CHILDREN_OFFSET = 0x00U,
    OPEN_CFW_LVGL_SPEC_SCROLL_X_OFFSET = 0x20U,
    OPEN_CFW_LVGL_SPEC_SCROLL_Y_OFFSET = 0x24U,
    OPEN_CFW_LVGL_SPEC_CHILD_COUNT_OFFSET = 0x30U,
    OPEN_CFW_LVGL_OBJ_LAYOUT_FLAGS_OFFSET = 0x2AU,
    OPEN_CFW_LVGL_W_LAYOUT_BIT = 11U,
    OPEN_CFW_LVGL_H_LAYOUT_BIT = 10U
};

/* Object byte access. Production is a direct cast (32-bit target);
 * host tests override these to translate test object ids. */
#ifndef OPEN_CFW_LVGL_OBJ_BYTES
#define OPEN_CFW_LVGL_OBJ_BYTES(obj) \
    ((const uint8_t *)(__UINTPTR_TYPE__)(obj))
#endif
#ifndef OPEN_CFW_LVGL_OBJ_BYTES_MUT
#define OPEN_CFW_LVGL_OBJ_BYTES_MUT(obj) \
    ((uint8_t *)(__UINTPTR_TYPE__)(obj))
#endif

/* Style getters owned by lvgl_layout_style_getters.c (same tranche). */
unsigned int open_cfw_lvgl_get_style_margin_left(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_margin_right(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_margin_top(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_margin_bottom(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_translate_x(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_translate_y(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_pad_left(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_pad_top(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_pad_row(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_pad_column(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_border_width(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_border_side(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_base_dir(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_width(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_height(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_column_align(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_row_align(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_column_dsc_array(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_row_dsc_array(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_cell_column_pos(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_cell_row_pos(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_cell_column_span(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_cell_row_span(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_cell_x_align(unsigned int obj, unsigned int part);
unsigned int open_cfw_lvgl_get_style_grid_cell_y_align(unsigned int obj, unsigned int part);

/* Retained-stock providers (addresses verified by disassembly; roles for
 * the deferred-grid callees are tracked for successor items). Each macro
 * is overridable so host tests can substitute doubles. */
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_GET_WIDTH
typedef int (*open_cfw_lvgl_retained_width_fn)(unsigned int obj);
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_WIDTH(obj) \
    (((open_cfw_lvgl_retained_width_fn)(__UINTPTR_TYPE__)0x0043FD9EU)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_GET_HEIGHT
typedef int (*open_cfw_lvgl_retained_height_fn)(unsigned int obj);
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_HEIGHT(obj) \
    (((open_cfw_lvgl_retained_height_fn)(__UINTPTR_TYPE__)0x0043FDDAU)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_GET_SCROLL_X
typedef int (*open_cfw_lvgl_retained_scroll_fn)(unsigned int obj);
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_SCROLL_X(obj) \
    (((open_cfw_lvgl_retained_scroll_fn)(__UINTPTR_TYPE__)0x0044E486U)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_GET_SCROLL_Y
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_SCROLL_Y(obj) \
    (((open_cfw_lvgl_retained_scroll_fn)(__UINTPTR_TYPE__)0x0044E498U)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_REFR_SIZE
typedef void (*open_cfw_lvgl_retained_refr_fn)(unsigned int obj);
#define OPEN_CFW_LVGL_RETAINED_OBJ_REFR_SIZE(obj) \
    (((open_cfw_lvgl_retained_refr_fn)(__UINTPTR_TYPE__)0x0043F1A4U)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_SEND_EVENT
typedef void (*open_cfw_lvgl_retained_event_fn)(unsigned int obj, unsigned int code, unsigned int param);
#define OPEN_CFW_LVGL_RETAINED_OBJ_SEND_EVENT(obj, code, param) \
    (((open_cfw_lvgl_retained_event_fn)(__UINTPTR_TYPE__)0x00451670U)((obj), (code), (param)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD
typedef unsigned int (*open_cfw_lvgl_retained_child_fn)(unsigned int obj, unsigned int idx);
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD(obj, idx) \
    (((open_cfw_lvgl_retained_child_fn)(__UINTPTR_TYPE__)0x0044DCE2U)((obj), (idx)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_WIDTH
typedef int (*open_cfw_lvgl_retained_content_fn)(unsigned int obj);
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_WIDTH(obj) \
    (((open_cfw_lvgl_retained_content_fn)(__UINTPTR_TYPE__)0x0043FE16U)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_HEIGHT
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_HEIGHT(obj) \
    (((open_cfw_lvgl_retained_content_fn)(__UINTPTR_TYPE__)0x0043FE70U)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_MEMSET
typedef void *(*open_cfw_lvgl_retained_memset_fn)(void *dst, unsigned int value, unsigned int len);
#define OPEN_CFW_LVGL_RETAINED_MEMSET(dst, value, len) \
    (((open_cfw_lvgl_retained_memset_fn)(__UINTPTR_TYPE__)0x00454746U)((dst), (value), (len)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_FREE
typedef void (*open_cfw_lvgl_retained_free_fn)(void *ptr);
#define OPEN_CFW_LVGL_RETAINED_FREE(ptr) \
    (((open_cfw_lvgl_retained_free_fn)(__UINTPTR_TYPE__)0x0044F758U)(ptr))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_GRID_CALC_COLS
typedef void (*open_cfw_lvgl_retained_bulk_fn)(unsigned int cont, open_cfw_lvgl_grid_calc_t *calc);
#define OPEN_CFW_LVGL_RETAINED_GRID_CALC_COLS(cont, calc) \
    (((open_cfw_lvgl_retained_bulk_fn)(__UINTPTR_TYPE__)0x0048CBF8U)((cont), (calc)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_GRID_CALC_ROWS
#define OPEN_CFW_LVGL_RETAINED_GRID_CALC_ROWS(cont, calc) \
    (((open_cfw_lvgl_retained_bulk_fn)(__UINTPTR_TYPE__)0x0048CDECU)((cont), (calc)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_GRID_ITEM_REPOS
typedef void (*open_cfw_lvgl_retained_repos_fn)(unsigned int item, open_cfw_lvgl_grid_calc_t *calc, open_cfw_lvgl_grid_hint_t *hint);
#define OPEN_CFW_LVGL_RETAINED_GRID_ITEM_REPOS(item, calc, hint) \
    (((open_cfw_lvgl_retained_repos_fn)(__UINTPTR_TYPE__)0x0048CFE0U)((item), (calc), (hint)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_GRID_ALIGN
typedef int (*open_cfw_lvgl_retained_align_fn)(int cont_size, unsigned int auto_size, unsigned int align, unsigned int gap, unsigned int track_num, void *sizes, void *positions, unsigned int reverse);
#define OPEN_CFW_LVGL_RETAINED_GRID_ALIGN(cont_size, auto_size, align, gap, track_num, sizes, positions, reverse) \
    (((open_cfw_lvgl_retained_align_fn)(__UINTPTR_TYPE__)0x0048D3C8U)((cont_size), (auto_size), (align), (gap), (track_num), (sizes), (positions), (reverse)))
#endif

/* Layout-registry anchor: the stock `lv_grid_init` body loads this base
 * from its literal pool word at 0x0048D3A0 and stores through slot
 * base+0x5C (cb at +0x10, user_data at +0x14). Overridable for hosts. */
#ifndef OPEN_CFW_LVGL_LAYOUT_REGISTRY_ANCHOR
#define OPEN_CFW_LVGL_LAYOUT_REGISTRY_ANCHOR 0x2006F548U
#endif
/* Stock entry address (Thumb bit set) this tranche's `grid_update`
 * occupies; stored by `lv_grid_init`, consumed by the layout
 * dispatcher. Pinned by the stock body hash in the host test. */
#ifndef OPEN_CFW_LVGL_GRID_UPDATE_ENTRY
#define OPEN_CFW_LVGL_GRID_UPDATE_ENTRY 0x0048CA3DU
#endif
enum {
    OPEN_CFW_LVGL_LAYOUT_SLOT_OFFSET = 0x5CU,
    OPEN_CFW_LVGL_LAYOUT_CB_OFFSET = 0x10U,
    OPEN_CFW_LVGL_LAYOUT_USER_DATA_OFFSET = 0x14U
};

/* Stock 0x0048C7B4: `lv_obj_get_width_with_margin` (lv_flex.c). */
__attribute__((used, noinline))
int open_cfw_lvgl_obj_get_width_with_margin(unsigned int obj)
{
    int margin_left =
        (int)open_cfw_lvgl_get_style_margin_left(obj, OPEN_CFW_LVGL_PART_MAIN);
    int width = OPEN_CFW_LVGL_RETAINED_OBJ_GET_WIDTH(obj);
    int margin_right =
        (int)open_cfw_lvgl_get_style_margin_right(obj, OPEN_CFW_LVGL_PART_MAIN);
    return margin_left + width + margin_right;
}

/* Stock 0x0048C7D8: `lv_obj_get_height_with_margin` (lv_flex.c). */
__attribute__((used, noinline))
int open_cfw_lvgl_obj_get_height_with_margin(unsigned int obj)
{
    int margin_top =
        (int)open_cfw_lvgl_get_style_margin_top(obj, OPEN_CFW_LVGL_PART_MAIN);
    int height = OPEN_CFW_LVGL_RETAINED_OBJ_GET_HEIGHT(obj);
    int margin_bottom =
        (int)open_cfw_lvgl_get_style_margin_bottom(obj, OPEN_CFW_LVGL_PART_MAIN);
    return margin_top + height + margin_bottom;
}

/* Stock 0x0048C7FC: `lv_area_copy` (lv_area.h). */
__attribute__((used, noinline))
void open_cfw_lvgl_area_copy(
    open_cfw_lvgl_grid_area_t *dest,
    const open_cfw_lvgl_grid_area_t *src
)
{
    dest->x1 = src->x1;
    dest->y1 = src->y1;
    dest->x2 = src->x2;
    dest->y2 = src->y2;
}

/* Stock 0x0048C80E: `lv_memzero` (lv_string.h) over retained `lv_memset`. */
__attribute__((used, noinline))
void open_cfw_lvgl_memzero(void *dest, unsigned int len)
{
    OPEN_CFW_LVGL_RETAINED_MEMSET(dest, 0U, len);
}

/* Stock 0x0048C920: `lv_obj_get_style_space_left` (lv_obj_style.h). */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_space_left(
    unsigned int obj,
    unsigned int part
)
{
    unsigned int padding = open_cfw_lvgl_get_style_pad_left(obj, part);
    unsigned int border_width = open_cfw_lvgl_get_style_border_width(obj, part);
    unsigned int border_side = open_cfw_lvgl_get_style_border_side(obj, part);
    return (border_side & OPEN_CFW_LVGL_BORDER_SIDE_LEFT) != 0U
        ? padding + border_width
        : padding;
}

/* Stock 0x0048C94E: `lv_obj_get_style_space_top` (lv_obj_style.h). */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_space_top(
    unsigned int obj,
    unsigned int part
)
{
    unsigned int padding = open_cfw_lvgl_get_style_pad_top(obj, part);
    unsigned int border_width = open_cfw_lvgl_get_style_border_width(obj, part);
    unsigned int border_side = open_cfw_lvgl_get_style_border_side(obj, part);
    return (border_side & OPEN_CFW_LVGL_BORDER_SIDE_TOP) != 0U
        ? padding + border_width
        : padding;
}

/* Stock 0x0048C97C: grid `get_col_dsc`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_col_dsc(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_column_dsc_array(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C986: grid `get_row_dsc`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_row_dsc(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_row_dsc_array(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C990: grid `get_col_pos`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_col_pos(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_cell_column_pos(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C99A: grid `get_row_pos`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_row_pos(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_cell_row_pos(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C9A4: grid `get_col_span`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_col_span(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_cell_column_span(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C9AE: grid `get_row_span`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_row_span(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_cell_row_span(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C9B8: grid `get_cell_col_align`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_cell_col_align(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_cell_x_align(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C9C2: grid `get_cell_row_align`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_cell_row_align(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_cell_y_align(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C9CC: grid `get_grid_col_align`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_grid_col_align(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_column_align(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C9D6: grid `get_grid_row_align`. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_get_grid_row_align(unsigned int obj)
{
    return open_cfw_lvgl_get_style_grid_row_align(obj, OPEN_CFW_LVGL_PART_MAIN);
}

/* Stock 0x0048C9E0: grid `get_margin_hor`. */
__attribute__((used, noinline))
int open_cfw_lvgl_grid_get_margin_hor(unsigned int obj)
{
    int margin_left =
        (int)open_cfw_lvgl_get_style_margin_left(obj, OPEN_CFW_LVGL_PART_MAIN);
    int margin_right =
        (int)open_cfw_lvgl_get_style_margin_right(obj, OPEN_CFW_LVGL_PART_MAIN);
    return margin_left + margin_right;
}

/* Stock 0x0048C9FC: grid `get_margin_ver`. */
__attribute__((used, noinline))
int open_cfw_lvgl_grid_get_margin_ver(unsigned int obj)
{
    int margin_top =
        (int)open_cfw_lvgl_get_style_margin_top(obj, OPEN_CFW_LVGL_PART_MAIN);
    int margin_bottom =
        (int)open_cfw_lvgl_get_style_margin_bottom(obj, OPEN_CFW_LVGL_PART_MAIN);
    return margin_top + margin_bottom;
}

/* Stock 0x0048CA18: grid `lv_div_round_closest` (truncating `sdiv`
 * semantics, matching C integer division). */
__attribute__((used, noinline))
int open_cfw_lvgl_grid_div_round_closest(int dividend, int divisor)
{
    return (dividend + divisor / 2) / divisor;
}

/* Stock 0x0048CA26: `lv_grid_init` (lv_grid.c). Registers this
 * tranche's `grid_update` through the layout-registry slot; the anchor
 * value reproduces the stock literal-pool word at 0x0048D3A0. */
__attribute__((used, noinline))
void open_cfw_lvgl_grid_init(void)
{
    unsigned int anchor = OPEN_CFW_LVGL_LAYOUT_REGISTRY_ANCHOR;
    unsigned int slot = *(const unsigned int *)(OPEN_CFW_LVGL_OBJ_BYTES(anchor) +
        OPEN_CFW_LVGL_LAYOUT_SLOT_OFFSET);
    *(unsigned int *)(OPEN_CFW_LVGL_OBJ_BYTES_MUT(slot) + OPEN_CFW_LVGL_LAYOUT_CB_OFFSET) =
        OPEN_CFW_LVGL_GRID_UPDATE_ENTRY;
    slot = *(const unsigned int *)(OPEN_CFW_LVGL_OBJ_BYTES(anchor) +
        OPEN_CFW_LVGL_LAYOUT_SLOT_OFFSET);
    *(unsigned int *)(OPEN_CFW_LVGL_OBJ_BYTES_MUT(slot) +
        OPEN_CFW_LVGL_LAYOUT_USER_DATA_OFFSET) = 0U;
}

/* Stock 0x0048CBDA: grid `calc_free` (lv_grid.c). */
__attribute__((used, noinline))
void open_cfw_lvgl_grid_calc_free(open_cfw_lvgl_grid_calc_t *calc)
{
    OPEN_CFW_LVGL_RETAINED_FREE(calc->x);
    OPEN_CFW_LVGL_RETAINED_FREE(calc->y);
    OPEN_CFW_LVGL_RETAINED_FREE(calc->w);
    OPEN_CFW_LVGL_RETAINED_FREE(calc->h);
}

/* Stock 0x0048D4D0: grid `count_tracks` (lv_grid.c). The stock body
 * leaves the count in r0 for its callers; the port returns it. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_grid_count_tracks(const unsigned int *templ)
{
    unsigned int i = 0U;
    while (templ[i] != OPEN_CFW_LVGL_GRID_TEMPLATE_LAST) {
        i += 1U;
    }
    return i;
}

/* Stock 0x0048CAD8: grid `calc` (lv_grid.c). */
__attribute__((used, noinline))
void open_cfw_lvgl_grid_calc(
    unsigned int cont,
    open_cfw_lvgl_grid_calc_t *calc_out
)
{
    if (OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD(cont, 0U) == 0U) {
        open_cfw_lvgl_memzero(calc_out, (unsigned int)sizeof(*calc_out));
        return;
    }

    OPEN_CFW_LVGL_RETAINED_GRID_CALC_ROWS(cont, calc_out);
    OPEN_CFW_LVGL_RETAINED_GRID_CALC_COLS(cont, calc_out);

    {
        unsigned int col_gap =
            open_cfw_lvgl_get_style_pad_column(cont, OPEN_CFW_LVGL_PART_MAIN);
        unsigned int row_gap =
            open_cfw_lvgl_get_style_pad_row(cont, OPEN_CFW_LVGL_PART_MAIN);
        unsigned int base_dir =
            open_cfw_lvgl_get_style_base_dir(cont, OPEN_CFW_LVGL_PART_MAIN);
        unsigned int w_set =
            open_cfw_lvgl_get_style_width(cont, OPEN_CFW_LVGL_PART_MAIN);
        unsigned int h_set =
            open_cfw_lvgl_get_style_height(cont, OPEN_CFW_LVGL_PART_MAIN);
        unsigned int layout_flags = (unsigned int)*(const uint16_t *)(
            OPEN_CFW_LVGL_OBJ_BYTES(cont) + OPEN_CFW_LVGL_OBJ_LAYOUT_FLAGS_OFFSET);
        unsigned int reverse = (base_dir == OPEN_CFW_LVGL_BASE_DIR_RTL) ? 1U : 0U;
        unsigned int auto_w =
            (w_set == OPEN_CFW_LVGL_SIZE_CONTENT &&
             (((layout_flags >> OPEN_CFW_LVGL_W_LAYOUT_BIT) & 1U) ^ 1U) != 0U)
            ? 1U
            : 0U;
        unsigned int auto_h =
            (h_set == OPEN_CFW_LVGL_SIZE_CONTENT &&
             (((layout_flags >> OPEN_CFW_LVGL_H_LAYOUT_BIT) & 1U) ^ 1U) != 0U)
            ? 1U
            : 0U;
        int cont_w = OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_WIDTH(cont);
        int cont_h = OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_HEIGHT(cont);
        unsigned int col_align = open_cfw_lvgl_grid_get_grid_col_align(cont);
        unsigned int row_align = open_cfw_lvgl_grid_get_grid_row_align(cont);

        calc_out->grid_w = OPEN_CFW_LVGL_RETAINED_GRID_ALIGN(
            cont_w, auto_w, col_align, col_gap, calc_out->col_num,
            calc_out->w, calc_out->x, reverse);
        calc_out->grid_h = OPEN_CFW_LVGL_RETAINED_GRID_ALIGN(
            cont_h, auto_h, row_align, row_gap, calc_out->row_num,
            calc_out->h, calc_out->y, 0U);
    }
}

/* Stock 0x0048CA3C: grid `grid_update` (lv_grid.c). */
__attribute__((used, noinline))
void open_cfw_lvgl_grid_update(unsigned int cont)
{
    open_cfw_lvgl_grid_calc_t calc;
    open_cfw_lvgl_grid_hint_t hint;
    unsigned int space_left =
        open_cfw_lvgl_get_style_space_left(cont, OPEN_CFW_LVGL_PART_MAIN);
    unsigned int space_top =
        open_cfw_lvgl_get_style_space_top(cont, OPEN_CFW_LVGL_PART_MAIN);
    int scroll_x = OPEN_CFW_LVGL_RETAINED_OBJ_GET_SCROLL_X(cont);
    int scroll_y = OPEN_CFW_LVGL_RETAINED_OBJ_GET_SCROLL_Y(cont);
    const uint8_t *coords =
        OPEN_CFW_LVGL_OBJ_BYTES(cont) + OPEN_CFW_LVGL_OBJ_COORDS_OFFSET;
    unsigned int i;

    open_cfw_lvgl_grid_calc(cont, &calc);
    open_cfw_lvgl_memzero(&hint, (unsigned int)sizeof(hint));

    hint.grid_abs_x = *(const int32_t *)(const void *)coords +
        (int32_t)space_left - scroll_x;
    hint.grid_abs_y = *(const int32_t *)(const void *)(coords + 4) +
        (int32_t)space_top - scroll_y;

    /* NOTE: the stock body reloads spec_attr/children/count every trip;
     * the reads are hoisted here because `item_repos` cannot mutate the
     * child vector under its upstream contract, so the trip sequence is
     * identical (see the audit). */
    {
        unsigned int spec_attr = *(const unsigned int *)(
            OPEN_CFW_LVGL_OBJ_BYTES(cont) + OPEN_CFW_LVGL_OBJ_SPEC_ATTR_OFFSET);
        unsigned int child_count = (unsigned int)*(const uint16_t *)(
            OPEN_CFW_LVGL_OBJ_BYTES(spec_attr) + OPEN_CFW_LVGL_SPEC_CHILD_COUNT_OFFSET);
        unsigned int children = *(const unsigned int *)(
            OPEN_CFW_LVGL_OBJ_BYTES(spec_attr) + OPEN_CFW_LVGL_SPEC_CHILDREN_OFFSET);
        for (i = 0U; i < child_count; i += 1U) {
            unsigned int item = *(const unsigned int *)(
                OPEN_CFW_LVGL_OBJ_BYTES(children) + i * (unsigned int)sizeof(unsigned int));
            OPEN_CFW_LVGL_RETAINED_GRID_ITEM_REPOS(item, &calc, &hint);
        }
    }

    open_cfw_lvgl_grid_calc_free(&calc);

    {
        unsigned int w_set =
            open_cfw_lvgl_get_style_width(cont, OPEN_CFW_LVGL_PART_MAIN);
        unsigned int h_set =
            open_cfw_lvgl_get_style_height(cont, OPEN_CFW_LVGL_PART_MAIN);
        if (w_set == OPEN_CFW_LVGL_SIZE_CONTENT ||
            h_set == OPEN_CFW_LVGL_SIZE_CONTENT) {
            OPEN_CFW_LVGL_RETAINED_OBJ_REFR_SIZE(cont);
        }
    }

    OPEN_CFW_LVGL_RETAINED_OBJ_SEND_EVENT(
        cont, OPEN_CFW_LVGL_EVENT_LAYOUT_CHANGED, 0U);
}

/* ---- Second-wave grid internals (stock 0x0048CBF8..0x0048D3A0 and
 * 0x0048D3C8): `calc_cols`, `calc_rows`, `item_repos`, `grid_align`.
 * Same upstream file, same retained-address technique; every default
 * below is overridable so host tests can substitute doubles. */

#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_GET_PARENT
typedef unsigned int (*open_cfw_lvgl_retained_parent_fn)(unsigned int obj);
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_PARENT(obj) \
    (((open_cfw_lvgl_retained_parent_fn)(__UINTPTR_TYPE__)0x0044DCA2U)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_HAS_FLAG_ANY
typedef int (*open_cfw_lvgl_retained_has_flag_fn)(unsigned int obj, unsigned int mask);
#define OPEN_CFW_LVGL_RETAINED_OBJ_HAS_FLAG_ANY(obj, mask) \
    (((open_cfw_lvgl_retained_has_flag_fn)(__UINTPTR_TYPE__)0x0043E11CU)((obj), (mask)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD_COUNT
typedef unsigned int (*open_cfw_lvgl_retained_child_count_fn)(unsigned int obj);
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD_COUNT(obj) \
    (((open_cfw_lvgl_retained_child_count_fn)(__UINTPTR_TYPE__)0x0044DDEAU)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_MALLOC
typedef void *(*open_cfw_lvgl_retained_malloc_fn)(unsigned int size);
#define OPEN_CFW_LVGL_RETAINED_MALLOC(size) \
    (((open_cfw_lvgl_retained_malloc_fn)(__UINTPTR_TYPE__)0x0044F718U)(size))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_MEMCPY
typedef void *(*open_cfw_lvgl_retained_memcpy_fn)(void *dst, const void *src, unsigned int len);
#define OPEN_CFW_LVGL_RETAINED_MEMCPY(dst, src, len) \
    (((open_cfw_lvgl_retained_memcpy_fn)(__UINTPTR_TYPE__)0x00454738U)((dst), (src), (len)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_INVALIDATE
typedef void (*open_cfw_lvgl_retained_invalidate_fn)(unsigned int obj);
#define OPEN_CFW_LVGL_RETAINED_OBJ_INVALIDATE(obj) \
    (((open_cfw_lvgl_retained_invalidate_fn)(__UINTPTR_TYPE__)0x00440656U)(obj))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_AREA_SET_WIDTH
typedef void (*open_cfw_lvgl_retained_area_set_fn)(void *area, int value);
#define OPEN_CFW_LVGL_RETAINED_AREA_SET_WIDTH(area, value) \
    (((open_cfw_lvgl_retained_area_set_fn)(__UINTPTR_TYPE__)0x00450B6CU)((area), (value)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_AREA_SET_HEIGHT
#define OPEN_CFW_LVGL_RETAINED_AREA_SET_HEIGHT(area, value) \
    (((open_cfw_lvgl_retained_area_set_fn)(__UINTPTR_TYPE__)0x00450B76U)((area), (value)))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_AREA_GET_WIDTH
typedef int (*open_cfw_lvgl_retained_area_get_fn)(const void *area);
#define OPEN_CFW_LVGL_RETAINED_AREA_GET_WIDTH(area) \
    (((open_cfw_lvgl_retained_area_get_fn)(__UINTPTR_TYPE__)0x00451598U)(area))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_AREA_GET_HEIGHT
#define OPEN_CFW_LVGL_RETAINED_AREA_GET_HEIGHT(area) \
    (((open_cfw_lvgl_retained_area_get_fn)(__UINTPTR_TYPE__)0x004515A4U)(area))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_OBJ_MOVE_CHILDREN_BY
typedef void (*open_cfw_lvgl_retained_move_children_fn)(unsigned int obj, int dx, int dy, unsigned int ignore);
#define OPEN_CFW_LVGL_RETAINED_OBJ_MOVE_CHILDREN_BY(obj, dx, dy, ignore) \
    (((open_cfw_lvgl_retained_move_children_fn)(__UINTPTR_TYPE__)0x0044035EU)((obj), (dx), (dy), (ignore)))
#endif
/* Template-array providers. Production dereferences the real grid style
 * getters (the stock bodies do exactly this: the getter returns the
 * array pointer in r0 and the caller indexes it). They are macros — not
 * direct calls — for one reason: on the 64-bit host the style core can
 * only return 32-bit values, which cannot round-trip a host array
 * pointer, so host tests substitute real host buffers here. The
 * getter-to-core forwarding itself is pinned by the wrapper tests. */
#ifndef OPEN_CFW_LVGL_GRID_COL_TEMPL
#define OPEN_CFW_LVGL_GRID_COL_TEMPL(cont) \
    ((const int *)(__UINTPTR_TYPE__)open_cfw_lvgl_grid_get_col_dsc(cont))
#endif
#ifndef OPEN_CFW_LVGL_GRID_ROW_TEMPL
#define OPEN_CFW_LVGL_GRID_ROW_TEMPL(cont) \
    ((const int *)(__UINTPTR_TYPE__)open_cfw_lvgl_grid_get_row_dsc(cont))
#endif
#ifndef OPEN_CFW_LVGL_RETAINED_LOG_WARN
typedef void (*open_cfw_lvgl_retained_log_fn)(
    int level, const char *file, int line, const char *func,
    const char *format
);
#define OPEN_CFW_LVGL_RETAINED_LOG_WARN(file, line, func, format) \
    (((open_cfw_lvgl_retained_log_fn)(__UINTPTR_TYPE__)0x0044D25CU)( \
        2, (file), (line), (func), (format)))
#endif

/* Stock rodata pointers consumed by the two subgrid-miss WARN calls
 * (literal-pool words at 0x0048D3A8..0x0048D3B0 / 0x0048D3C0..0x0048D3C4;
 * the file path names the vendor fork's own `lv_grid.c`). */
#ifndef OPEN_CFW_LVGL_GRID_WARN_FILE
#define OPEN_CFW_LVGL_GRID_WARN_FILE ((const char *)(__UINTPTR_TYPE__)0x006E079CU)
#endif
#ifndef OPEN_CFW_LVGL_GRID_CALC_COLS_FUNC
#define OPEN_CFW_LVGL_GRID_CALC_COLS_FUNC ((const char *)(__UINTPTR_TYPE__)0x0078AEECU)
#endif
#ifndef OPEN_CFW_LVGL_GRID_CALC_ROWS_FUNC
#define OPEN_CFW_LVGL_GRID_CALC_ROWS_FUNC ((const char *)(__UINTPTR_TYPE__)0x0078AEF8U)
#endif
#ifndef OPEN_CFW_LVGL_GRID_CALC_COLS_WARN_FORMAT
#define OPEN_CFW_LVGL_GRID_CALC_COLS_WARN_FORMAT ((const char *)(__UINTPTR_TYPE__)0x0073F5ACU)
#endif
#ifndef OPEN_CFW_LVGL_GRID_CALC_ROWS_WARN_FORMAT
#define OPEN_CFW_LVGL_GRID_CALC_ROWS_WARN_FORMAT ((const char *)(__UINTPTR_TYPE__)0x0073F5D8U)
#endif

enum {
    OPEN_CFW_LVGL_GRID_FR_BASE = 0x1FFFFF9BU,
    OPEN_CFW_LVGL_GRID_CONTENT = 0x1FFFFF9AU,
    OPEN_CFW_LVGL_LAYOUT_IGNORE_MASK = 0x00060001U,
    OPEN_CFW_LVGL_GRID_ALIGN_START = 0U,
    OPEN_CFW_LVGL_GRID_ALIGN_CENTER = 1U,
    OPEN_CFW_LVGL_GRID_ALIGN_END = 2U,
    OPEN_CFW_LVGL_GRID_ALIGN_STRETCH = 3U,
    OPEN_CFW_LVGL_GRID_ALIGN_SPACE_EVENLY = 4U,
    OPEN_CFW_LVGL_GRID_ALIGN_SPACE_AROUND = 5U,
    OPEN_CFW_LVGL_GRID_ALIGN_SPACE_BETWEEN = 6U,
    OPEN_CFW_LVGL_COORD_MIN = 0xE0000001U,
    OPEN_CFW_LVGL_EVENT_SIZE_CHANGED = 0x31U,
    OPEN_CFW_LVGL_EVENT_CHILD_CHANGED = 0x2AU
};

/* Stock 0x0048CBF8: grid `calc_cols` (lv_grid.c). Sizes every column
 * track: CONTENT tracks take the widest single-span visible child,
 * fixed tracks keep their template value, FR tracks split the
 * remaining content width via `lv_div_round_closest`. The NULL-template
 * path borrows the parent slice (subgrid) and frees it on exit; the
 * double-NULL path warns (LV_LOG_LEVEL_WARN, line 0x11D) and returns.
 * Upstream returns void; the stock body's trailing r0 (content width)
 * is a leftover no caller consumes (`calc` discards it), so the port
 * returns void as well. */
__attribute__((used, noinline))
void open_cfw_lvgl_grid_calc_cols(
    unsigned int cont,
    open_cfw_lvgl_grid_calc_t *calc
)
{
    const int *col_templ;
    unsigned int subgrid = 0U;
    int cont_w;
    unsigned int col_fr_count = 0U;
    int grid_w = 0;
    int col_gap;
    int free_w;
    unsigned int i;

    col_templ = OPEN_CFW_LVGL_GRID_COL_TEMPL(cont);
    if (col_templ == NULL) {
        unsigned int parent = OPEN_CFW_LVGL_RETAINED_OBJ_GET_PARENT(cont);
        int pos;
        int span;
        unsigned int *sub;
        col_templ = OPEN_CFW_LVGL_GRID_COL_TEMPL(parent);
        if (col_templ == NULL) {
            OPEN_CFW_LVGL_RETAINED_LOG_WARN(
                OPEN_CFW_LVGL_GRID_WARN_FILE, 0x11D,
                OPEN_CFW_LVGL_GRID_CALC_COLS_FUNC,
                OPEN_CFW_LVGL_GRID_CALC_COLS_WARN_FORMAT);
            return;
        }
        pos = (int)open_cfw_lvgl_grid_get_col_pos(cont);
        span = (int)open_cfw_lvgl_grid_get_col_span(cont);
        sub = (unsigned int *)OPEN_CFW_LVGL_RETAINED_MALLOC(
            (unsigned int)(span + 1) * 4U);
        OPEN_CFW_LVGL_RETAINED_MEMCPY(
            sub, (const void *)(col_templ + pos),
            (unsigned int)span * 4U);
        sub[span] = OPEN_CFW_LVGL_GRID_TEMPLATE_LAST;
        col_templ = (const int *)sub;
        subgrid = 1U;
    }

    cont_w = OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_WIDTH(cont);
    calc->col_num = open_cfw_lvgl_grid_count_tracks(
        (const unsigned int *)col_templ);
    calc->x = OPEN_CFW_LVGL_RETAINED_MALLOC(calc->col_num * 4U);
    calc->w = OPEN_CFW_LVGL_RETAINED_MALLOC(calc->col_num * 4U);

    /* NOTE: as in `grid_update`, the child count is read once; the
     * skipped/measured children cannot mutate the vector under the
     * upstream contract, so the trip sequence is identical. */
    {
        unsigned int child_count =
            OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD_COUNT(cont);
        for (i = 0U; i < calc->col_num; i += 1U) {
            if (col_templ[i] == (int)OPEN_CFW_LVGL_GRID_CONTENT) {
                int size = (int)OPEN_CFW_LVGL_COORD_MIN;
                unsigned int ci;
                for (ci = 0U; ci < child_count; ci += 1U) {
                    unsigned int item =
                        OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD(cont, ci);
                    int item_w;
                    if (OPEN_CFW_LVGL_RETAINED_OBJ_HAS_FLAG_ANY(
                            item, OPEN_CFW_LVGL_LAYOUT_IGNORE_MASK) != 0) {
                        continue;
                    }
                    if (open_cfw_lvgl_grid_get_col_span(item) != 1U) {
                        continue;
                    }
                    if (open_cfw_lvgl_grid_get_col_pos(item) != i) {
                        continue;
                    }
                    item_w = OPEN_CFW_LVGL_RETAINED_OBJ_GET_WIDTH(item);
                    if (item_w > size) {
                        size = item_w;
                    }
                }
                ((int *)calc->w)[i] = size >= 0 ? size : 0;
            }
        }
    }

    for (i = 0U; i < calc->col_num; i += 1U) {
        int templ = col_templ[i];
        if (templ >= (int)OPEN_CFW_LVGL_GRID_FR_BASE) {
            col_fr_count += (unsigned int)(templ - (int)OPEN_CFW_LVGL_GRID_FR_BASE);
        }
        else if (templ == (int)OPEN_CFW_LVGL_GRID_CONTENT) {
            grid_w += ((int *)calc->w)[i];
        }
        else {
            ((int *)calc->w)[i] = templ;
            grid_w += templ;
        }
    }

    col_gap = (int)open_cfw_lvgl_get_style_pad_column(
        cont, OPEN_CFW_LVGL_PART_MAIN);
    free_w = (cont_w - (int)(calc->col_num - 1U) * col_gap) - grid_w;
    if (free_w < 0) {
        free_w = 0;
    }

    for (i = 0U; i < calc->col_num && col_fr_count != 0U; i += 1U) {
        int templ = col_templ[i];
        if (templ >= (int)OPEN_CFW_LVGL_GRID_FR_BASE) {
            unsigned int fr =
                (unsigned int)(templ - (int)OPEN_CFW_LVGL_GRID_FR_BASE);
            ((int *)calc->w)[i] = open_cfw_lvgl_grid_div_round_closest(
                (int)((unsigned int)free_w * fr), (int)col_fr_count);
            col_fr_count -= fr;
            free_w -= ((int *)calc->w)[i];
        }
    }

    if (subgrid != 0U) {
        OPEN_CFW_LVGL_RETAINED_FREE((void *)col_templ);
    }
}

/* Stock 0x0048CDEC: grid `calc_rows` (lv_grid.c), the row twin of
 * `calc_cols` (pad_row gap, content height, heights; WARN line 0x179).
 * Same void-return note as `calc_cols` (the stock trailing word is
 * caller-discarded garbage). */
__attribute__((used, noinline))
void open_cfw_lvgl_grid_calc_rows(
    unsigned int cont,
    open_cfw_lvgl_grid_calc_t *calc
)
{
    const int *row_templ;
    unsigned int subgrid = 0U;
    int cont_h;
    unsigned int row_fr_count = 0U;
    int grid_h = 0;
    int row_gap;
    int free_h;
    unsigned int i;

    row_templ = OPEN_CFW_LVGL_GRID_ROW_TEMPL(cont);
    if (row_templ == NULL) {
        unsigned int parent = OPEN_CFW_LVGL_RETAINED_OBJ_GET_PARENT(cont);
        int pos;
        int span;
        unsigned int *sub;
        row_templ = OPEN_CFW_LVGL_GRID_ROW_TEMPL(parent);
        if (row_templ == NULL) {
            OPEN_CFW_LVGL_RETAINED_LOG_WARN(
                OPEN_CFW_LVGL_GRID_WARN_FILE, 0x179,
                OPEN_CFW_LVGL_GRID_CALC_ROWS_FUNC,
                OPEN_CFW_LVGL_GRID_CALC_ROWS_WARN_FORMAT);
            return;
        }
        pos = (int)open_cfw_lvgl_grid_get_row_pos(cont);
        span = (int)open_cfw_lvgl_grid_get_row_span(cont);
        sub = (unsigned int *)OPEN_CFW_LVGL_RETAINED_MALLOC(
            (unsigned int)(span + 1) * 4U);
        OPEN_CFW_LVGL_RETAINED_MEMCPY(
            sub, (const void *)(row_templ + pos),
            (unsigned int)span * 4U);
        sub[span] = OPEN_CFW_LVGL_GRID_TEMPLATE_LAST;
        row_templ = (const int *)sub;
        subgrid = 1U;
    }

    calc->row_num = open_cfw_lvgl_grid_count_tracks(
        (const unsigned int *)row_templ);
    calc->y = OPEN_CFW_LVGL_RETAINED_MALLOC(calc->row_num * 4U);
    calc->h = OPEN_CFW_LVGL_RETAINED_MALLOC(calc->row_num * 4U);

    {
        unsigned int child_count =
            OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD_COUNT(cont);
        for (i = 0U; i < calc->row_num; i += 1U) {
            if (row_templ[i] == (int)OPEN_CFW_LVGL_GRID_CONTENT) {
                int size = (int)OPEN_CFW_LVGL_COORD_MIN;
                unsigned int ci;
                for (ci = 0U; ci < child_count; ci += 1U) {
                    unsigned int item =
                        OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD(cont, ci);
                    int item_h;
                    if (OPEN_CFW_LVGL_RETAINED_OBJ_HAS_FLAG_ANY(
                            item, OPEN_CFW_LVGL_LAYOUT_IGNORE_MASK) != 0) {
                        continue;
                    }
                    if (open_cfw_lvgl_grid_get_row_span(item) != 1U) {
                        continue;
                    }
                    if (open_cfw_lvgl_grid_get_row_pos(item) != i) {
                        continue;
                    }
                    item_h = OPEN_CFW_LVGL_RETAINED_OBJ_GET_HEIGHT(item);
                    if (item_h > size) {
                        size = item_h;
                    }
                }
                ((int *)calc->h)[i] = size >= 0 ? size : 0;
            }
        }
    }

    for (i = 0U; i < calc->row_num; i += 1U) {
        int templ = row_templ[i];
        if (templ >= (int)OPEN_CFW_LVGL_GRID_FR_BASE) {
            row_fr_count += (unsigned int)(templ - (int)OPEN_CFW_LVGL_GRID_FR_BASE);
        }
        else if (templ == (int)OPEN_CFW_LVGL_GRID_CONTENT) {
            grid_h += ((int *)calc->h)[i];
        }
        else {
            ((int *)calc->h)[i] = templ;
            grid_h += templ;
        }
    }

    row_gap = (int)open_cfw_lvgl_get_style_pad_row(
        cont, OPEN_CFW_LVGL_PART_MAIN);
    cont_h = OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_HEIGHT(cont);
    free_h = (cont_h - (int)(calc->row_num - 1U) * row_gap) - grid_h;
    if (free_h < 0) {
        free_h = 0;
    }

    for (i = 0U; i < calc->row_num && row_fr_count != 0U; i += 1U) {
        int templ = row_templ[i];
        if (templ >= (int)OPEN_CFW_LVGL_GRID_FR_BASE) {
            unsigned int fr =
                (unsigned int)(templ - (int)OPEN_CFW_LVGL_GRID_FR_BASE);
            ((int *)calc->h)[i] = open_cfw_lvgl_grid_div_round_closest(
                (int)((unsigned int)free_h * fr), (int)row_fr_count);
            row_fr_count -= fr;
            free_h -= ((int *)calc->h)[i];
        }
    }

    if (subgrid != 0U) {
        OPEN_CFW_LVGL_RETAINED_FREE((void *)row_templ);
    }
}

/* Stock 0x0048CFE0: grid `item_repos` (lv_grid.c). Repositions one
 * grid item in its cell: flag/span guards, RTL start/end mirror,
 * START/CENTER/END/STRETCH placement per axis (STRETCH sets the
 * w_layout bit 11 / h_layout bit 10 at obj+0x2A, the others clear
 * it), size-change invalidate/resize/event sequence
 * (LV_EVENT_SIZE_CHANGED 0x31, LV_EVENT_CHILD_CHANGED 0x2A), percent
 * translate handling per LV_COORD_IS_PCT/LV_COORD_GET_PCT, and the
 * grid-origin move via `lv_obj_move_children_by(item, dx, dy, 0)`.
 * Out-of-range aligns (> STRETCH, e.g. the SPACE_* values) fall into
 * the START path exactly as the stock branch structure does. */
__attribute__((used, noinline))
void open_cfw_lvgl_grid_item_repos(
    unsigned int item,
    open_cfw_lvgl_grid_calc_t *calc,
    open_cfw_lvgl_grid_hint_t *hint
)
{
    unsigned int col_span;
    unsigned int row_span;
    unsigned int col_pos;
    unsigned int row_pos;
    unsigned int col_align;
    unsigned int row_align;
    const uint8_t *item_bytes;
    const int *calc_x;
    const int *calc_y;
    const int *calc_w;
    const int *calc_h;
    int col_w;
    int row_h;
    int item_w;
    int item_h;
    int x;
    int y;
    uint16_t layout_flags;

    if (OPEN_CFW_LVGL_RETAINED_OBJ_HAS_FLAG_ANY(
            item, OPEN_CFW_LVGL_LAYOUT_IGNORE_MASK) != 0) {
        return;
    }
    col_span = open_cfw_lvgl_grid_get_col_span(item);
    row_span = open_cfw_lvgl_grid_get_row_span(item);
    if (row_span == 0U || col_span == 0U) {
        return;
    }

    col_pos = open_cfw_lvgl_grid_get_col_pos(item);
    row_pos = open_cfw_lvgl_grid_get_row_pos(item);
    col_align = open_cfw_lvgl_grid_get_cell_col_align(item);
    row_align = open_cfw_lvgl_grid_get_cell_row_align(item);

    calc_x = (const int *)calc->x;
    calc_y = (const int *)calc->y;
    calc_w = (const int *)calc->w;
    calc_h = (const int *)calc->h;
    col_w = (calc_x[col_pos + col_span - 1U] + calc_w[col_pos + col_span - 1U]) -
        calc_x[col_pos];
    row_h = (calc_y[row_pos + row_span - 1U] + calc_h[row_pos + row_span - 1U]) -
        calc_y[row_pos];

    if (open_cfw_lvgl_get_style_base_dir(item, OPEN_CFW_LVGL_PART_MAIN) ==
        OPEN_CFW_LVGL_BASE_DIR_RTL) {
        if (col_align == OPEN_CFW_LVGL_GRID_ALIGN_START) {
            col_align = OPEN_CFW_LVGL_GRID_ALIGN_END;
        }
        else if (col_align == OPEN_CFW_LVGL_GRID_ALIGN_END) {
            col_align = OPEN_CFW_LVGL_GRID_ALIGN_START;
        }
    }

    item_bytes = OPEN_CFW_LVGL_OBJ_BYTES(item);
    item_w = OPEN_CFW_LVGL_RETAINED_AREA_GET_WIDTH(
        (const void *)(item_bytes + OPEN_CFW_LVGL_OBJ_COORDS_OFFSET));
    item_h = OPEN_CFW_LVGL_RETAINED_AREA_GET_HEIGHT(
        (const void *)(item_bytes + OPEN_CFW_LVGL_OBJ_COORDS_OFFSET));
    layout_flags = *(const uint16_t *)(const void *)(
        item_bytes + OPEN_CFW_LVGL_OBJ_LAYOUT_FLAGS_OFFSET);

    if (col_align == OPEN_CFW_LVGL_GRID_ALIGN_CENTER) {
        int margin_left = (int)open_cfw_lvgl_get_style_margin_left(
            item, OPEN_CFW_LVGL_PART_MAIN);
        int margin_right = (int)open_cfw_lvgl_get_style_margin_right(
            item, OPEN_CFW_LVGL_PART_MAIN);
        x = calc_x[col_pos] + (col_w - item_w) / 2 +
            (margin_left - margin_right) / 2;
        layout_flags = (uint16_t)(layout_flags & 0xF7FFU);
    }
    else if (col_align == OPEN_CFW_LVGL_GRID_ALIGN_START) {
        x = calc_x[col_pos] + (int)open_cfw_lvgl_get_style_margin_left(
            item, OPEN_CFW_LVGL_PART_MAIN);
        layout_flags = (uint16_t)(layout_flags & 0xF7FFU);
    }
    else if (col_align == OPEN_CFW_LVGL_GRID_ALIGN_STRETCH) {
        x = calc_x[col_pos] + (int)open_cfw_lvgl_get_style_margin_left(
            item, OPEN_CFW_LVGL_PART_MAIN);
        item_w = col_w - open_cfw_lvgl_grid_get_margin_hor(item);
        layout_flags = (uint16_t)(layout_flags | 0x0800U);
    }
    else if (col_align == OPEN_CFW_LVGL_GRID_ALIGN_END) {
        x = (calc_x[col_pos] + col_w) -
            OPEN_CFW_LVGL_RETAINED_OBJ_GET_WIDTH(item) -
            (int)open_cfw_lvgl_get_style_margin_right(
                item, OPEN_CFW_LVGL_PART_MAIN);
        layout_flags = (uint16_t)(layout_flags & 0xF7FFU);
    }
    else {
        x = calc_x[col_pos] + (int)open_cfw_lvgl_get_style_margin_left(
            item, OPEN_CFW_LVGL_PART_MAIN);
        layout_flags = (uint16_t)(layout_flags & 0xF7FFU);
    }
    *(uint16_t *)(OPEN_CFW_LVGL_OBJ_BYTES_MUT(item) +
        OPEN_CFW_LVGL_OBJ_LAYOUT_FLAGS_OFFSET) = layout_flags;

    if (row_align == OPEN_CFW_LVGL_GRID_ALIGN_CENTER) {
        int margin_top = (int)open_cfw_lvgl_get_style_margin_top(
            item, OPEN_CFW_LVGL_PART_MAIN);
        int margin_bottom = (int)open_cfw_lvgl_get_style_margin_bottom(
            item, OPEN_CFW_LVGL_PART_MAIN);
        y = calc_y[row_pos] + (row_h - item_h) / 2 +
            (margin_top - margin_bottom) / 2;
        layout_flags = (uint16_t)(layout_flags & 0xFBFFU);
    }
    else if (row_align == OPEN_CFW_LVGL_GRID_ALIGN_START) {
        y = calc_y[row_pos] + (int)open_cfw_lvgl_get_style_margin_top(
            item, OPEN_CFW_LVGL_PART_MAIN);
        layout_flags = (uint16_t)(layout_flags & 0xFBFFU);
    }
    else if (row_align == OPEN_CFW_LVGL_GRID_ALIGN_STRETCH) {
        y = calc_y[row_pos] + (int)open_cfw_lvgl_get_style_margin_top(
            item, OPEN_CFW_LVGL_PART_MAIN);
        item_h = row_h - open_cfw_lvgl_grid_get_margin_ver(item);
        layout_flags = (uint16_t)(layout_flags | 0x0400U);
    }
    else if (row_align == OPEN_CFW_LVGL_GRID_ALIGN_END) {
        y = (calc_y[row_pos] + row_h) -
            OPEN_CFW_LVGL_RETAINED_OBJ_GET_HEIGHT(item) -
            (int)open_cfw_lvgl_get_style_margin_bottom(
                item, OPEN_CFW_LVGL_PART_MAIN);
        layout_flags = (uint16_t)(layout_flags & 0xFBFFU);
    }
    else {
        y = calc_y[row_pos] + (int)open_cfw_lvgl_get_style_margin_top(
            item, OPEN_CFW_LVGL_PART_MAIN);
        layout_flags = (uint16_t)(layout_flags & 0xFBFFU);
    }
    *(uint16_t *)(OPEN_CFW_LVGL_OBJ_BYTES_MUT(item) +
        OPEN_CFW_LVGL_OBJ_LAYOUT_FLAGS_OFFSET) = layout_flags;

    if (OPEN_CFW_LVGL_RETAINED_OBJ_GET_WIDTH(item) != item_w ||
        OPEN_CFW_LVGL_RETAINED_OBJ_GET_HEIGHT(item) != item_h) {
        open_cfw_lvgl_grid_area_t old_coords;
        unsigned int parent;
        open_cfw_lvgl_area_copy(
            &old_coords,
            (const open_cfw_lvgl_grid_area_t *)(const void *)(
                OPEN_CFW_LVGL_OBJ_BYTES(item) +
                OPEN_CFW_LVGL_OBJ_COORDS_OFFSET));
        OPEN_CFW_LVGL_RETAINED_OBJ_INVALIDATE(item);
        OPEN_CFW_LVGL_RETAINED_AREA_SET_WIDTH(
            (void *)(OPEN_CFW_LVGL_OBJ_BYTES_MUT(item) +
                OPEN_CFW_LVGL_OBJ_COORDS_OFFSET),
            item_w);
        OPEN_CFW_LVGL_RETAINED_AREA_SET_HEIGHT(
            (void *)(OPEN_CFW_LVGL_OBJ_BYTES_MUT(item) +
                OPEN_CFW_LVGL_OBJ_COORDS_OFFSET),
            item_h);
        OPEN_CFW_LVGL_RETAINED_OBJ_INVALIDATE(item);
        OPEN_CFW_LVGL_RETAINED_OBJ_SEND_EVENT(
            item, OPEN_CFW_LVGL_EVENT_SIZE_CHANGED,
            (unsigned int)(__UINTPTR_TYPE__)&old_coords);
        parent = OPEN_CFW_LVGL_RETAINED_OBJ_GET_PARENT(item);
        OPEN_CFW_LVGL_RETAINED_OBJ_SEND_EVENT(
            parent, OPEN_CFW_LVGL_EVENT_CHILD_CHANGED, item);
    }

    {
        unsigned int tr_x = open_cfw_lvgl_get_style_translate_x(
            item, OPEN_CFW_LVGL_PART_MAIN);
        unsigned int tr_y = open_cfw_lvgl_get_style_translate_y(
            item, OPEN_CFW_LVGL_PART_MAIN);
        int w = OPEN_CFW_LVGL_RETAINED_OBJ_GET_WIDTH(item);
        int h = OPEN_CFW_LVGL_RETAINED_OBJ_GET_HEIGHT(item);
        if ((tr_x & 0x60000000U) == 0x20000000U &&
            (int)(tr_x & 0x9FFFFFFFU) < (int)OPEN_CFW_LVGL_GRID_TEMPLATE_LAST) {
            unsigned int plain = tr_x & 0x9FFFFFFFU;
            unsigned int pct = plain < 0x10000000U
                ? plain
                : 0x0FFFFFFFU - plain;
            tr_x = (unsigned int)((int)(pct * (unsigned int)w) / 100);
        }
        if ((tr_y & 0x60000000U) == 0x20000000U &&
            (int)(tr_y & 0x9FFFFFFFU) < (int)OPEN_CFW_LVGL_GRID_TEMPLATE_LAST) {
            unsigned int plain = tr_y & 0x9FFFFFFFU;
            unsigned int pct = plain < 0x10000000U
                ? plain
                : 0x0FFFFFFFU - plain;
            tr_y = (unsigned int)((int)(pct * (unsigned int)h) / 100);
        }
        x += (int)tr_x;
        y += (int)tr_y;
    }

    {
        const int *coords = (const int *)(const void *)(
            OPEN_CFW_LVGL_OBJ_BYTES(item) +
            OPEN_CFW_LVGL_OBJ_COORDS_OFFSET);
        int diff_x = (hint->grid_abs_x + x) - coords[0];
        int diff_y = (hint->grid_abs_y + y) - coords[1];
        if (diff_x != 0 || diff_y != 0) {
            int *mut_coords = (int *)(OPEN_CFW_LVGL_OBJ_BYTES_MUT(item) +
                OPEN_CFW_LVGL_OBJ_COORDS_OFFSET);
            OPEN_CFW_LVGL_RETAINED_OBJ_INVALIDATE(item);
            mut_coords[0] += diff_x;
            mut_coords[2] += diff_x;
            mut_coords[1] += diff_y;
            mut_coords[3] += diff_y;
            OPEN_CFW_LVGL_RETAINED_OBJ_INVALIDATE(item);
            OPEN_CFW_LVGL_RETAINED_OBJ_MOVE_CHILDREN_BY(item, diff_x, diff_y, 0U);
        }
    }
}

/* Stock 0x0048D3C8: grid `grid_align` (lv_grid.c). Places one axis of
 * tracks: auto-size pins the first track at zero, spaced aligns first
 * zero the gap (a lone track degrades to CENTER), then the first
 * position per align case, chained positions, the total span return,
 * and the optional RTL mirror. Faithful to the stock body including
 * its unsigned `track_num - 1` trip bound. */
__attribute__((used, noinline))
int open_cfw_lvgl_grid_align(
    int cont_size,
    unsigned int auto_size,
    unsigned int align,
    int gap,
    unsigned int track_num,
    int *sizes,
    int *positions,
    unsigned int reverse
)
{
    int grid_size = 0;
    unsigned int i;

    if (auto_size == 0U) {
        if (align == OPEN_CFW_LVGL_GRID_ALIGN_SPACE_AROUND ||
            align == OPEN_CFW_LVGL_GRID_ALIGN_SPACE_BETWEEN ||
            align == OPEN_CFW_LVGL_GRID_ALIGN_SPACE_EVENLY) {
            gap = 0;
            if (track_num == 1U) {
                align = OPEN_CFW_LVGL_GRID_ALIGN_CENTER;
            }
        }

        for (i = 0U; i < track_num; i += 1U) {
            grid_size += sizes[i] + gap;
        }
        grid_size -= gap;

        if (align == OPEN_CFW_LVGL_GRID_ALIGN_START) {
            positions[0] = 0;
        }
        else if (align == OPEN_CFW_LVGL_GRID_ALIGN_CENTER) {
            positions[0] = (cont_size - grid_size) / 2;
        }
        else if (align == OPEN_CFW_LVGL_GRID_ALIGN_END) {
            positions[0] = cont_size - grid_size;
        }
        else if (align == OPEN_CFW_LVGL_GRID_ALIGN_SPACE_EVENLY) {
            gap = (cont_size - grid_size) / (int)(track_num + 1U);
            positions[0] = gap;
        }
        else if (align == OPEN_CFW_LVGL_GRID_ALIGN_SPACE_AROUND) {
            gap = (cont_size - grid_size) / (int)track_num;
            positions[0] = gap / 2;
        }
        else if (align == OPEN_CFW_LVGL_GRID_ALIGN_SPACE_BETWEEN) {
            positions[0] = 0;
            gap = (cont_size - grid_size) / (int)(track_num - 1U);
        }
    }
    else {
        positions[0] = 0;
    }

    for (i = 0U; i < track_num - 1U; i += 1U) {
        positions[i + 1U] = positions[i] + sizes[i] + gap;
    }

    {
        int total = positions[track_num - 1U] + sizes[track_num - 1U] -
            positions[0];
        if (reverse != 0U) {
            for (i = 0U; i < track_num; i += 1U) {
                positions[i] = (cont_size - positions[i]) - sizes[i];
            }
        }
        return total;
    }
}
