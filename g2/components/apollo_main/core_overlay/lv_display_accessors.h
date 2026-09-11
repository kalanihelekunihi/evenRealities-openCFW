/*
 * SPDX-License-Identifier: MIT
 *
 * Minimal ABI subset of the stock G2 2.2.6.10 LVGL v9.3 `lv_display_t`
 * object, recovered field-by-field from the Thumb-2 decompilation of the
 * accessor/mutator leaves this component replaces. See
 * `lv_display_accessors.c` and `docs/research/g2-lvgl-display-accessors.md`.
 *
 * Only fields actually read or written by an admitted leaf are named; every
 * other byte range is declared `reserved` padding and MUST NOT be given
 * semantic meaning without new decompilation evidence.
 */

#ifndef OPEN_CFW_LV_DISPLAY_ACCESSORS_H
#define OPEN_CFW_LV_DISPLAY_ACCESSORS_H

#include <stdint.h>

typedef struct open_cfw_lv_display {
    int32_t hor_res;              /* 0x00 */
    int32_t ver_res;              /* 0x04 */
    int32_t physical_hor_res;     /* 0x08 */
    int32_t physical_ver_res;     /* 0x0c */
    int32_t offset_x;             /* 0x10 */
    int32_t offset_y;             /* 0x14 */
    uint32_t dpi;                 /* 0x18 */
    void *buf_1;                  /* 0x1c */
    void *buf_2;                  /* 0x20 */
    void *buf_act;                /* 0x24 */
    uint32_t word_field;          /* 0x28 */
    uint8_t reserved_0x2c[8];     /* 0x2c..0x33 */
    uint32_t render_flag;         /* 0x34 */
    uint8_t reserved_0x38;        /* 0x38 */
    uint8_t byte_flag;            /* 0x39 */
    uint8_t reserved_0x3a[642];   /* 0x3a..0x2bb */
    void *invalidate_target;      /* 0x2bc */
    uint8_t reserved_0x2c0[60];   /* 0x2c0..0x2fb */
    uint32_t rotation;            /* 0x2fc (only bits 0..2 read) */
} open_cfw_lv_display_t;

unsigned int open_cfw_lv_display_set_offset(
    open_cfw_lv_display_t *display,
    unsigned int x,
    unsigned int y,
    unsigned int unused_return
);
int32_t open_cfw_lv_display_get_horizontal_resolution(
    open_cfw_lv_display_t *display
);
int32_t open_cfw_lv_display_get_vertical_resolution(
    open_cfw_lv_display_t *display
);
int32_t open_cfw_lv_display_get_physical_horizontal_resolution(
    open_cfw_lv_display_t *display
);
int32_t open_cfw_lv_display_get_physical_vertical_resolution(
    open_cfw_lv_display_t *display
);
int32_t open_cfw_lv_display_get_offset_x(open_cfw_lv_display_t *display);
int32_t open_cfw_lv_display_get_offset_y(open_cfw_lv_display_t *display);
uint32_t open_cfw_lv_display_get_dpi(open_cfw_lv_display_t *display);
unsigned int open_cfw_lv_display_set_buffers_internal(
    open_cfw_lv_display_t *display,
    void *buf_1,
    void *buf_2,
    unsigned int unused_return
);
void open_cfw_lv_display_set_byte_flag(
    open_cfw_lv_display_t *display,
    uint8_t value
);
void open_cfw_lv_display_set_word_field(
    open_cfw_lv_display_t *display,
    uint32_t value
);
unsigned char open_cfw_lv_display_get_render_flag(
    const open_cfw_lv_display_t *display
);
unsigned char open_cfw_lv_display_is_double_buffered(
    const open_cfw_lv_display_t *display
);

#endif /* OPEN_CFW_LV_DISPLAY_ACCESSORS_H */
