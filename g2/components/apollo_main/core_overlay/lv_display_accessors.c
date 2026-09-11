/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room replacement for thirteen G2 2.2.6.10 LVGL v9.3 `lv_display_t`
 * accessor/mutator leaves at stock entries 0x0044FA5E..0x0044FC62.
 *
 * These are internal (non-exported, non-`LV_API`) helpers of LVGL's
 * `src/display/lv_display.c`.  No vendored copy of that file is present in
 * this tree, so the struct layout below is not the authoritative LVGL
 * header: it is a minimal ABI subset recovered directly from the stock
 * Thumb-2 decompilation (`g2/research/corpus/apollo-main/ghidra/decomp`)
 * and pinned by `g2/tools/manifests/g2-lvgl-vendor-fork-census.tsv`, which
 * attributes every one of these entries to `LVGL/src/display/lv_display.c`.
 * Each field offset below is exactly the offset the stock code reads or
 * writes; the gaps are declared `reserved` padding and are never accessed by
 * this file. `g2/tools/emulate_g2_lvgl_display_accessors.py` differentially
 * executes each real stock body against the C below under Unicorn, across
 * many synthetic struct states, and requires an exact match of returned
 * register, external-call trace, and object-memory writes; see
 * `g2/docs/research/g2-lvgl-display-accessors.md`.
 *
 * The public LVGL v9.3 behavior these mirror is documented upstream at
 * https://github.com/lvgl/lvgl (MIT License, Copyright (c) 2021 LVGL Kft.);
 * this file is an independent, from-scratch reimplementation of the observed
 * stock behavior, not a copy of any LVGL source file.
 */

#include <stdint.h>

#include "lv_display_accessors.h"

/*
 * Two callees outside this leaf's stock range remain retained elsewhere in
 * the official Apollo application image (they are not part of the
 * 0x0044FA5E..0x004501D2 span this file replaces and are tracked by other
 * work items). They are invoked here through their exact stock ABI, exactly
 * as the surrounding still-retained code and other already-admitted
 * openCFW sources (e.g. `lv_display_lock.c`, `lv_display_sync.c`) already
 * do for their own out-of-range callees.
 */
#ifndef OPEN_CFW_LV_DISPLAY_GET_DEFAULT
typedef void *(*open_cfw_lv_display_get_default_fn)(void);
#define OPEN_CFW_LV_DISPLAY_GET_DEFAULT() \
    (((open_cfw_lv_display_get_default_fn)0x0044FA1BU)())
#endif

#ifndef OPEN_CFW_LV_DISPLAY_INVALIDATE
typedef void (*open_cfw_lv_display_invalidate_fn)(void *target);
#define OPEN_CFW_LV_DISPLAY_INVALIDATE(target) \
    (((open_cfw_lv_display_invalidate_fn)0x00440657U)((target)))
#endif

/*
 * Each accessor below is compiled and admitted as its own dependency-free
 * overlay leaf (see overlay.json), matching the stock layout in which every
 * one of these is its own standalone function. `resolve` is therefore kept
 * force-inlined rather than emitted as a shared helper symbol, and the two
 * accessors that call a stock sibling in this same admitted set (offset_x
 * and offset_y calling the physical-resolution pair) do so through the
 * sibling's own exact stock entry address, exactly like the two genuinely
 * out-of-range callees above. Once every sibling in this file is patched in
 * at its stock address, that address resolves to this file's replacement,
 * the same way any other caller of that stock address would be redirected.
 */
static inline __attribute__((always_inline)) open_cfw_lv_display_t *
open_cfw_lv_display_resolve(open_cfw_lv_display_t *display)
{
    if (display == (open_cfw_lv_display_t *)0) {
        display = (open_cfw_lv_display_t *)OPEN_CFW_LV_DISPLAY_GET_DEFAULT();
    }
    return display;
}

#ifndef OPEN_CFW_LV_DISPLAY_GET_PHYSICAL_HORIZONTAL_RESOLUTION
typedef int32_t (*open_cfw_lv_display_get_phys_fn)(void *display);
#define OPEN_CFW_LV_DISPLAY_GET_PHYSICAL_HORIZONTAL_RESOLUTION(display) \
    (((open_cfw_lv_display_get_phys_fn)0x0044FAD3U)((display)))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_GET_PHYSICAL_VERTICAL_RESOLUTION
#define OPEN_CFW_LV_DISPLAY_GET_PHYSICAL_VERTICAL_RESOLUTION(display) \
    (((open_cfw_lv_display_get_phys_fn)0x0044FB11U)((display)))
#endif

unsigned int open_cfw_lv_display_set_offset(
    open_cfw_lv_display_t *display,
    unsigned int x,
    unsigned int y,
    unsigned int unused_return
)
{
    display = open_cfw_lv_display_resolve(display);
    if (display != (open_cfw_lv_display_t *)0) {
        display->offset_x = (int32_t)x;
        display->offset_y = (int32_t)y;
        OPEN_CFW_LV_DISPLAY_INVALIDATE(display->invalidate_target);
    }
    return unused_return;
}

int32_t open_cfw_lv_display_get_horizontal_resolution(
    open_cfw_lv_display_t *display
)
{
    display = open_cfw_lv_display_resolve(display);
    if (display == (open_cfw_lv_display_t *)0) {
        return 0;
    }
    if ((display->rotation & 7U) == 1U || (display->rotation & 7U) == 3U) {
        return display->ver_res;
    }
    return display->hor_res;
}

int32_t open_cfw_lv_display_get_vertical_resolution(
    open_cfw_lv_display_t *display
)
{
    display = open_cfw_lv_display_resolve(display);
    if (display == (open_cfw_lv_display_t *)0) {
        return 0;
    }
    if ((display->rotation & 7U) == 1U || (display->rotation & 7U) == 3U) {
        return display->hor_res;
    }
    return display->ver_res;
}

int32_t open_cfw_lv_display_get_physical_horizontal_resolution(
    open_cfw_lv_display_t *display
)
{
    display = open_cfw_lv_display_resolve(display);
    if (display == (open_cfw_lv_display_t *)0) {
        return 0;
    }
    if ((display->rotation & 7U) == 1U || (display->rotation & 7U) == 3U) {
        return (display->physical_ver_res < 1)
            ? display->ver_res
            : display->physical_ver_res;
    }
    return (display->physical_hor_res < 1)
        ? display->hor_res
        : display->physical_hor_res;
}

int32_t open_cfw_lv_display_get_physical_vertical_resolution(
    open_cfw_lv_display_t *display
)
{
    display = open_cfw_lv_display_resolve(display);
    if (display == (open_cfw_lv_display_t *)0) {
        return 0;
    }
    if ((display->rotation & 7U) == 1U || (display->rotation & 7U) == 3U) {
        return (display->physical_hor_res < 1)
            ? display->hor_res
            : display->physical_hor_res;
    }
    return (display->physical_ver_res < 1)
        ? display->ver_res
        : display->physical_ver_res;
}

int32_t open_cfw_lv_display_get_offset_x(open_cfw_lv_display_t *display)
{
    unsigned int rotation;

    display = open_cfw_lv_display_resolve(display);
    if (display == (open_cfw_lv_display_t *)0) {
        return 0;
    }
    rotation = display->rotation & 7U;
    if (rotation == 1U) {
        return display->offset_y;
    }
    if (rotation != 0U) {
        if (rotation == 3U) {
            return OPEN_CFW_LV_DISPLAY_GET_PHYSICAL_HORIZONTAL_RESOLUTION(
                display
            ) - display->offset_y;
        }
        if (rotation < 3U) {
            return OPEN_CFW_LV_DISPLAY_GET_PHYSICAL_HORIZONTAL_RESOLUTION(
                display
            ) - display->offset_x;
        }
    }
    return display->offset_x;
}

int32_t open_cfw_lv_display_get_offset_y(open_cfw_lv_display_t *display)
{
    unsigned int rotation;

    display = open_cfw_lv_display_resolve(display);
    if (display == (open_cfw_lv_display_t *)0) {
        return 0;
    }
    rotation = display->rotation & 7U;
    if (rotation == 1U) {
        return display->offset_x;
    }
    if (rotation != 0U) {
        if (rotation == 3U) {
            return OPEN_CFW_LV_DISPLAY_GET_PHYSICAL_VERTICAL_RESOLUTION(
                display
            ) - display->offset_x;
        }
        if (rotation < 3U) {
            return OPEN_CFW_LV_DISPLAY_GET_PHYSICAL_VERTICAL_RESOLUTION(
                display
            ) - display->offset_y;
        }
    }
    return display->offset_y;
}

uint32_t open_cfw_lv_display_get_dpi(open_cfw_lv_display_t *display)
{
    display = open_cfw_lv_display_resolve(display);
    if (display == (open_cfw_lv_display_t *)0) {
        return 0x82U;
    }
    return display->dpi;
}

unsigned int open_cfw_lv_display_set_buffers_internal(
    open_cfw_lv_display_t *display,
    void *buf_1,
    void *buf_2,
    unsigned int unused_return
)
{
    display = open_cfw_lv_display_resolve(display);
    if (display != (open_cfw_lv_display_t *)0) {
        display->buf_1 = buf_1;
        display->buf_2 = buf_2;
        display->buf_act = display->buf_1;
    }
    return unused_return;
}

void open_cfw_lv_display_set_byte_flag(
    open_cfw_lv_display_t *display,
    uint8_t value
)
{
    display = open_cfw_lv_display_resolve(display);
    if (display != (open_cfw_lv_display_t *)0) {
        display->byte_flag = value;
    }
}

void open_cfw_lv_display_set_word_field(
    open_cfw_lv_display_t *display,
    uint32_t value
)
{
    display = open_cfw_lv_display_resolve(display);
    if (display != (open_cfw_lv_display_t *)0) {
        display->word_field = value;
    }
}

/*
 * These last two have no stock null-check/default fallback: the stock
 * bodies dereference the argument directly. Preserve that exactly rather
 * than adding defensive behavior the original does not have.
 */
unsigned char open_cfw_lv_display_get_render_flag(
    const open_cfw_lv_display_t *display
)
{
    return display->render_flag != 0;
}

unsigned char open_cfw_lv_display_is_double_buffered(
    const open_cfw_lv_display_t *display
)
{
    return display->buf_2 != (void *)0;
}
