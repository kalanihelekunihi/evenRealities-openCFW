/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of twenty-five LVGL 9.3 style-property getters
 * retained in G2 firmware 2.2.6.10 at 0x0048C81A..0x0048C920 (Apollo main
 * application, component `apollo_main`, work item AM-040).
 *
 * Every function here is a thin two-argument (`obj`, `part`) forward to the
 * shared style-lookup core `lv_obj_get_style_prop` (FUN_0044BDEA, outside
 * this item's range and still a retained-stock callee), each passing a
 * distinct `lv_style_prop_t` literal. Six of them (the `lv_grid_align_t` /
 * `lv_border_side_t` / `lv_base_dir_t` enum returns) narrow the core's
 * 32-bit result to one byte first (`uxtb r0, r0` in the stock bodies);
 * the rest forward the full 32-bit / pointer result untouched. This is
 * exactly the shape of the upstream `static inline` wrappers in
 * third_party/lvgl/src/core/lv_obj_style_gen.h, which the stock IAR build
 * left out-of-line.
 *
 * Property IDs are confirmed against the official LVGL 9.3-dev interval
 * 60d976c..344c7c (github.com/lvgl/lvgl) `src/misc/lv_style.h` enum,
 * which the G2 firmware is independently pinned to by
 * docs/research/lvgl-version-recovery-audit.md:
 *
 *   0x01 LV_STYLE_WIDTH                0x1B LV_STYLE_MARGIN_RIGHT
 *   0x02 LV_STYLE_HEIGHT               0x27 LV_STYLE_BASE_DIR
 *   0x10 LV_STYLE_PAD_TOP              0x30 LV_STYLE_BORDER_WIDTH
 *   0x12 LV_STYLE_PAD_LEFT             0x34 LV_STYLE_BORDER_SIDE
 *   0x14 LV_STYLE_PAD_ROW              0x6C LV_STYLE_TRANSLATE_X
 *   0x15 LV_STYLE_PAD_COLUMN           0x6D LV_STYLE_TRANSLATE_Y
 *   0x18 LV_STYLE_MARGIN_TOP           0x7F LV_STYLE_GRID_COLUMN_ALIGN
 *   0x19 LV_STYLE_MARGIN_BOTTOM        0x80 LV_STYLE_GRID_ROW_ALIGN
 *   0x1A LV_STYLE_MARGIN_LEFT          0x81 LV_STYLE_GRID_ROW_DSC_ARRAY
 *   0x1B (see right column)            0x82 LV_STYLE_GRID_COLUMN_DSC_ARRAY
 *   0x83 LV_STYLE_GRID_CELL_COLUMN_POS 0x87 LV_STYLE_GRID_CELL_ROW_SPAN
 *   0x84 LV_STYLE_GRID_CELL_COLUMN_SPAN
 *   0x85 LV_STYLE_GRID_CELL_X_ALIGN    0x88 LV_STYLE_GRID_CELL_Y_ALIGN
 *   0x86 LV_STYLE_GRID_CELL_ROW_POS
 *
 * The grid-family getters (0x7F..0x88) are consumed by the grid layout
 * engine recovered in lvgl_grid_engine.c; the pad/margin/border/base-dir
 * getters feed its space/width-with-margin composites.
 */

typedef unsigned int open_cfw_lvgl_layout_getter_pointer;

#ifndef OPEN_CFW_LVGL_LAYOUT_GETTER_CORE
typedef unsigned int (*open_cfw_lvgl_layout_getter_core_fn)(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part,
    unsigned int property
);
#define OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(obj, part, property) \
    (((open_cfw_lvgl_layout_getter_core_fn)(__UINTPTR_TYPE__)0x0044BDEBU)( \
        (obj), (part), (property) \
    ))
#endif

enum {
    OPEN_CFW_LVGL_PROP_WIDTH = 0x01U,
    OPEN_CFW_LVGL_PROP_HEIGHT = 0x02U,
    OPEN_CFW_LVGL_PROP_RECOVERED_0A = 0x0AU,
    OPEN_CFW_LVGL_PROP_PAD_TOP = 0x10U,
    OPEN_CFW_LVGL_PROP_PAD_LEFT = 0x12U,
    OPEN_CFW_LVGL_PROP_PAD_ROW = 0x14U,
    OPEN_CFW_LVGL_PROP_PAD_COLUMN = 0x15U,
    OPEN_CFW_LVGL_PROP_MARGIN_TOP = 0x18U,
    OPEN_CFW_LVGL_PROP_MARGIN_BOTTOM = 0x19U,
    OPEN_CFW_LVGL_PROP_MARGIN_LEFT = 0x1AU,
    OPEN_CFW_LVGL_PROP_MARGIN_RIGHT = 0x1BU,
    OPEN_CFW_LVGL_PROP_BASE_DIR = 0x27U,
    OPEN_CFW_LVGL_PROP_BORDER_WIDTH = 0x30U,
    OPEN_CFW_LVGL_PROP_BORDER_SIDE = 0x34U,
    OPEN_CFW_LVGL_PROP_TRANSLATE_X = 0x6CU,
    OPEN_CFW_LVGL_PROP_TRANSLATE_Y = 0x6DU,
    OPEN_CFW_LVGL_PROP_RECOVERED_6A = 0x6AU,
    OPEN_CFW_LVGL_PROP_GRID_COLUMN_ALIGN = 0x7FU,
    OPEN_CFW_LVGL_PROP_GRID_ROW_ALIGN = 0x80U,
    OPEN_CFW_LVGL_PROP_GRID_ROW_DSC_ARRAY = 0x81U,
    OPEN_CFW_LVGL_PROP_GRID_COLUMN_DSC_ARRAY = 0x82U,
    OPEN_CFW_LVGL_PROP_GRID_CELL_COLUMN_POS = 0x83U,
    OPEN_CFW_LVGL_PROP_GRID_CELL_COLUMN_SPAN = 0x84U,
    OPEN_CFW_LVGL_PROP_GRID_CELL_X_ALIGN = 0x85U,
    OPEN_CFW_LVGL_PROP_GRID_CELL_ROW_POS = 0x86U,
    OPEN_CFW_LVGL_PROP_GRID_CELL_ROW_SPAN = 0x87U,
    OPEN_CFW_LVGL_PROP_GRID_CELL_Y_ALIGN = 0x88U
};

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_width(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_WIDTH
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_height(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_HEIGHT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_width_am002(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_WIDTH
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_height_am002(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_HEIGHT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_recovered_0a_am002(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return (unsigned int)(unsigned char)OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_RECOVERED_0A
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_recovered_6a_am002(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_RECOVERED_6A
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_translate_x(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_TRANSLATE_X
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_translate_y(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_TRANSLATE_Y
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_pad_top(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_PAD_TOP
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_pad_left(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_PAD_LEFT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_pad_row(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_PAD_ROW
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_pad_column(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_PAD_COLUMN
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_margin_top(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_MARGIN_TOP
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_margin_bottom(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_MARGIN_BOTTOM
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_margin_left(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_MARGIN_LEFT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_margin_right(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_MARGIN_RIGHT
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_border_width(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_BORDER_WIDTH
    );
}

/* Stock 0x0048C89C narrows the core result with `uxtb` (12 bytes);
 * LV_STYLE_BORDER_SIDE is an `lv_border_side_t` enum. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_border_side(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return (unsigned int)(unsigned char)OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_BORDER_SIDE
    );
}

/* Stock 0x0048C8A8 narrows the core result with `uxtb` (12 bytes);
 * LV_STYLE_BASE_DIR is an `lv_base_dir_t` enum. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_base_dir(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return (unsigned int)(unsigned char)OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_BASE_DIR
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_column_dsc_array(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_COLUMN_DSC_ARRAY
    );
}

/* Stock 0x0048C8BE narrows the core result with `uxtb` (12 bytes);
 * LV_STYLE_GRID_COLUMN_ALIGN is an `lv_grid_align_t` enum. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_column_align(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return (unsigned int)(unsigned char)OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_COLUMN_ALIGN
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_row_dsc_array(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_ROW_DSC_ARRAY
    );
}

/* Stock 0x0048C8D4 narrows the core result with `uxtb` (12 bytes);
 * LV_STYLE_GRID_ROW_ALIGN is an `lv_grid_align_t` enum. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_row_align(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return (unsigned int)(unsigned char)OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_ROW_ALIGN
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_cell_column_pos(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_CELL_COLUMN_POS
    );
}

/* Stock 0x0048C8EA narrows the core result with `uxtb` (12 bytes);
 * LV_STYLE_GRID_CELL_X_ALIGN is an `lv_grid_align_t` enum. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_cell_x_align(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return (unsigned int)(unsigned char)OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_CELL_X_ALIGN
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_cell_column_span(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_CELL_COLUMN_SPAN
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_cell_row_pos(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_CELL_ROW_POS
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_cell_row_span(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_CELL_ROW_SPAN
    );
}

/* Stock 0x0048C90A narrows the core result with `uxtb` (12 bytes);
 * LV_STYLE_GRID_CELL_Y_ALIGN is an `lv_grid_align_t` enum. */
__attribute__((used, noinline))
unsigned int open_cfw_lvgl_get_style_grid_cell_y_align(
    open_cfw_lvgl_layout_getter_pointer obj,
    unsigned int part
)
{
    return (unsigned int)(unsigned char)OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(
        obj, part, OPEN_CFW_LVGL_PROP_GRID_CELL_Y_ALIGN
    );
}
