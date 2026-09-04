/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 generic production-test screen.
 * Diagnostic logging is intentionally omitted. The registered data-handler
 * ABI, predicate, LVGL object construction, geometry, colors, and both root
 * publications are preserved.
 */
#include "production_test_screen.h"

typedef uint32_t open_cfw_production_test_color;

void *open_cfw_retained_production_test_object_create(void *parent);
void open_cfw_retained_production_test_clear_flags(
    void *object, uint32_t flags
);
void open_cfw_retained_production_test_set_width(
    void *object, int32_t width
);
void open_cfw_retained_production_test_set_height(
    void *object, int32_t height
);
void open_cfw_retained_production_test_set_size(
    void *object, int32_t width, int32_t height
);
void open_cfw_retained_production_test_set_pos(
    void *object, int32_t x, int32_t y
);
open_cfw_production_test_color open_cfw_retained_production_test_color_hex(
    uint32_t rgb
);
open_cfw_production_test_color open_cfw_retained_production_test_color_make(
    uint32_t red, uint32_t green, uint32_t blue
);
void open_cfw_retained_production_test_set_bg_color(
    void *object, open_cfw_production_test_color color, uint32_t selector
);
void open_cfw_retained_production_test_set_bg_opacity(
    void *object, uint32_t opacity, uint32_t selector
);
void open_cfw_retained_production_test_set_border_color(
    void *object, open_cfw_production_test_color color, uint32_t selector
);
void open_cfw_retained_production_test_set_border_width(
    void *object, int32_t width, uint32_t selector
);

#ifndef OPEN_CFW_PRODUCTION_TEST_ROOT
#define OPEN_CFW_PRODUCTION_TEST_ROOT \
    (*(void * volatile *)0x20074894U)
#endif

#ifndef OPEN_CFW_PRODUCTION_TEST_REGISTRY_ROOT
#define OPEN_CFW_PRODUCTION_TEST_REGISTRY_ROOT \
    (*(void * volatile *)0x200030A4U)
#endif

#if defined(OPEN_CFW_PRODUCTION_TEST_COMMON_DATA_ONLY)
#define OPEN_CFW_PRODUCTION_TEST_SELECTOR 1
#elif defined(OPEN_CFW_PRODUCTION_TEST_PREDICATE_ONLY)
#define OPEN_CFW_PRODUCTION_TEST_SELECTOR 2
#elif defined(OPEN_CFW_PRODUCTION_TEST_SCREEN_EVENT_ONLY)
#define OPEN_CFW_PRODUCTION_TEST_SELECTOR 3
#elif !defined(OPEN_CFW_PRODUCTION_TEST_SELECTOR)
#define OPEN_CFW_PRODUCTION_TEST_SELECTOR 0
#endif

#define OPEN_CFW_PRODUCTION_TEST_BUILD(number) \
    (OPEN_CFW_PRODUCTION_TEST_SELECTOR == 0 || \
     OPEN_CFW_PRODUCTION_TEST_SELECTOR == (number))

#if defined(__arm__) || defined(__thumb__)
__asm__(
    ".type open_cfw_production_test_common_data_handler,%function\n"
    ".type open_cfw_production_test_predicate,%function\n"
    ".type open_cfw_production_test_screen_event,%function\n"
);
#endif

#if OPEN_CFW_PRODUCTION_TEST_BUILD(1)
__attribute__((used, noinline))
int open_cfw_production_test_common_data_handler(
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

#if OPEN_CFW_PRODUCTION_TEST_BUILD(2)
__attribute__((used, noinline))
int open_cfw_production_test_predicate(void)
{
    return 1;
}
#endif

#if OPEN_CFW_PRODUCTION_TEST_BUILD(3)
__attribute__((used, noinline))
int open_cfw_production_test_screen_event(
    uint32_t event,
    const void *argument_1,
    const void *argument_2,
    void *parent
)
{
    void *root;
    void *dot;
    open_cfw_production_test_color black;
    open_cfw_production_test_color white;
    int32_t row;
    int32_t column;

    (void)argument_1;
    (void)argument_2;
    if (event != OPEN_CFW_PRODUCTION_TEST_CONSTRUCT_EVENT) {
        return 0;
    }

    root = open_cfw_retained_production_test_object_create(parent);
    OPEN_CFW_PRODUCTION_TEST_ROOT = root;
    open_cfw_retained_production_test_clear_flags(root, 0x10U);
    open_cfw_retained_production_test_set_width(root, 640);
    open_cfw_retained_production_test_set_height(root, 480);
    open_cfw_retained_production_test_clear_flags(root, 0x10U);

    black = open_cfw_retained_production_test_color_hex(0U);
    open_cfw_retained_production_test_set_bg_color(root, black, 0U);
    open_cfw_retained_production_test_set_bg_opacity(root, 255U, 0U);
    open_cfw_retained_production_test_set_border_color(root, black, 0U);

    white = open_cfw_retained_production_test_color_make(255U, 255U, 255U);
    for (row = 0; row < 3; ++row) {
        for (column = 0; column < 3; ++column) {
            dot = open_cfw_retained_production_test_object_create(root);
            open_cfw_retained_production_test_set_size(dot, 10, 10);
            open_cfw_retained_production_test_set_bg_color(dot, white, 0U);
            open_cfw_retained_production_test_set_border_width(dot, 0, 0U);
            open_cfw_retained_production_test_set_pos(
                dot, 66 + 200 * column, 21 + 100 * row
            );
        }
    }

    OPEN_CFW_PRODUCTION_TEST_REGISTRY_ROOT = root;
    return 0;
}
#endif
