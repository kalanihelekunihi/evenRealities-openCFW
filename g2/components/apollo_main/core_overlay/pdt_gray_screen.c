/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 production gray screen. Diagnostic
 * logging is intentionally omitted. The registered callback ABI, LVGL object
 * construction, geometry, symmetric gray ramp, and root publications are
 * preserved.
 */
#include "pdt_gray_screen.h"

typedef uint32_t open_cfw_pdt_gray_color;

void *open_cfw_retained_pdt_gray_object_create(void *parent);
void open_cfw_retained_pdt_gray_clear_flags(void *object, uint32_t flags);
void open_cfw_retained_pdt_gray_set_width(void *object, int32_t width);
void open_cfw_retained_pdt_gray_set_height(void *object, int32_t height);
void open_cfw_retained_pdt_gray_set_size(
    void *object, int32_t width, int32_t height
);
void open_cfw_retained_pdt_gray_set_pos(
    void *object, int32_t x, int32_t y
);
open_cfw_pdt_gray_color open_cfw_retained_pdt_gray_color_hex(uint32_t rgb);
open_cfw_pdt_gray_color open_cfw_retained_pdt_gray_color_make(
    uint32_t red, uint32_t green, uint32_t blue
);
void open_cfw_retained_pdt_gray_set_bg_color(
    void *object, open_cfw_pdt_gray_color color, uint32_t selector
);
void open_cfw_retained_pdt_gray_set_bg_opacity(
    void *object, uint32_t opacity, uint32_t selector
);
void open_cfw_retained_pdt_gray_set_border_color(
    void *object, open_cfw_pdt_gray_color color, uint32_t selector
);
void open_cfw_retained_pdt_gray_set_border_width(
    void *object, int32_t width, uint32_t selector
);
void open_cfw_retained_pdt_gray_set_scrollbar_mode(
    void *object, uint32_t mode
);

#ifndef OPEN_CFW_PDT_GRAY_ROOT
#define OPEN_CFW_PDT_GRAY_ROOT (*(void * volatile *)0x20074880U)
#endif

#ifndef OPEN_CFW_PDT_GRAY_REGISTRY_ROOT
#define OPEN_CFW_PDT_GRAY_REGISTRY_ROOT (*(void * volatile *)0x20003084U)
#endif

#if defined(OPEN_CFW_PDT_GRAY_COMMON_DATA_ONLY)
#define OPEN_CFW_PDT_GRAY_SELECTOR 1
#elif defined(OPEN_CFW_PDT_GRAY_PREDICATE_ONLY)
#define OPEN_CFW_PDT_GRAY_SELECTOR 2
#elif defined(OPEN_CFW_PDT_GRAY_SCREEN_EVENT_ONLY)
#define OPEN_CFW_PDT_GRAY_SELECTOR 3
#elif !defined(OPEN_CFW_PDT_GRAY_SELECTOR)
#define OPEN_CFW_PDT_GRAY_SELECTOR 0
#endif

#define OPEN_CFW_PDT_GRAY_BUILD(number) \
    (OPEN_CFW_PDT_GRAY_SELECTOR == 0 || \
     OPEN_CFW_PDT_GRAY_SELECTOR == (number))

#if defined(__arm__) || defined(__thumb__)
__asm__(
    ".type open_cfw_pdt_gray_common_data_handler,%function\n"
    ".type open_cfw_pdt_gray_predicate,%function\n"
    ".type open_cfw_pdt_gray_screen_event,%function\n"
);
#endif

#if OPEN_CFW_PDT_GRAY_BUILD(1)
__attribute__((used, noinline))
int open_cfw_pdt_gray_common_data_handler(
    const void *context,
    const void *data,
    uint32_t length
)
{
    (void)context;
    (void)data;
    (void)length;
    return 0;
}
#endif

#if OPEN_CFW_PDT_GRAY_BUILD(2)
__attribute__((used, noinline))
int open_cfw_pdt_gray_predicate(void)
{
    return 1;
}
#endif

#if OPEN_CFW_PDT_GRAY_BUILD(3)
__attribute__((used, noinline))
int open_cfw_pdt_gray_screen_event(
    uint32_t event,
    const void *argument_1,
    const void *argument_2,
    void *parent
)
{
    void *root;
    void *band;
    open_cfw_pdt_gray_color black;
    open_cfw_pdt_gray_color gray;
    uint32_t index;
    uint32_t exponent;
    uint32_t value;

    (void)argument_1;
    (void)argument_2;
    if (event != OPEN_CFW_PDT_GRAY_CONSTRUCT_EVENT) {
        return 0;
    }

    root = open_cfw_retained_pdt_gray_object_create(parent);
    OPEN_CFW_PDT_GRAY_ROOT = root;
    open_cfw_retained_pdt_gray_clear_flags(root, 0x10U);
    open_cfw_retained_pdt_gray_set_width(root, 640);
    open_cfw_retained_pdt_gray_set_height(root, 480);
    open_cfw_retained_pdt_gray_clear_flags(root, 0x10U);
    black = open_cfw_retained_pdt_gray_color_hex(0U);
    open_cfw_retained_pdt_gray_set_bg_color(root, black, 0U);
    open_cfw_retained_pdt_gray_set_bg_opacity(root, 255U, 0U);
    open_cfw_retained_pdt_gray_set_border_color(root, black, 0U);

    for (index = 0U; index < 8U; ++index) {
        band = open_cfw_retained_pdt_gray_object_create(root);
        open_cfw_retained_pdt_gray_clear_flags(band, 0x10U);
        open_cfw_retained_pdt_gray_set_size(band, 72, 288);
        open_cfw_retained_pdt_gray_set_pos(band, 72 * (int32_t)index, 0);
        open_cfw_retained_pdt_gray_set_border_width(band, 0, 0U);
        open_cfw_retained_pdt_gray_set_scrollbar_mode(band, 0U);
        exponent = index <= 3U ? index : 7U - index;
        value = 17U << exponent;
        gray = open_cfw_retained_pdt_gray_color_make(value, value, value);
        open_cfw_retained_pdt_gray_set_bg_color(band, gray, 0U);
        open_cfw_retained_pdt_gray_set_bg_opacity(band, 255U, 0U);
    }

    OPEN_CFW_PDT_GRAY_REGISTRY_ROOT = root;
    return 0;
}
#endif
