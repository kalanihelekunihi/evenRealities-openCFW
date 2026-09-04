/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 production distortion-test screen.
 * Diagnostic logging is intentionally omitted. The registered callback ABI,
 * nested LVGL layout, resource lookup, style contract, and root publications
 * are preserved.
 */
#include "pdt_distortion_test.h"

#include <stdint.h>

typedef uint32_t open_cfw_pdt_distortion_color;

void *open_cfw_retained_pdt_distortion_object_create(void *parent);
void open_cfw_retained_pdt_distortion_clear_flags(
    void *object, uint32_t flags
);
void open_cfw_retained_pdt_distortion_add_flags(
    void *object, uint32_t flags
);
void open_cfw_retained_pdt_distortion_set_width(
    void *object, int32_t width
);
void open_cfw_retained_pdt_distortion_set_height(
    void *object, int32_t height
);
void open_cfw_retained_pdt_distortion_set_size(
    void *object, int32_t width, int32_t height
);
void open_cfw_retained_pdt_distortion_set_pos(
    void *object, int32_t x, int32_t y
);
void open_cfw_retained_pdt_distortion_align(
    void *object, uint32_t alignment, int32_t x, int32_t y
);
open_cfw_pdt_distortion_color open_cfw_retained_pdt_distortion_color_hex(
    uint32_t rgb
);
void open_cfw_retained_pdt_distortion_set_bg_color(
    void *object, open_cfw_pdt_distortion_color color, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_bg_opacity(
    void *object, uint32_t opacity, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_border_color(
    void *object, open_cfw_pdt_distortion_color color, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_border_opacity(
    void *object, uint32_t opacity, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_border_width(
    void *object, int32_t width, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_shadow_color(
    void *object, open_cfw_pdt_distortion_color color, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_shadow_opacity(
    void *object, uint32_t opacity, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_style_0(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_style_1(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_style_2(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_style_3(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_layout_gap_0(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_layout_gap_1(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_frame_style_0(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_frame_style_1(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_frame_style_2(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_frame_style_3(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_frame_style_4(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_frame_style_5(
    void *object, uint32_t value, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_scrollbar_mode(
    void *object, uint32_t mode
);
void open_cfw_retained_pdt_distortion_set_flex_flow(
    void *object, uint32_t flow
);
void open_cfw_retained_pdt_distortion_set_flex_align(
    void *object, uint32_t main_place, uint32_t cross_place,
    uint32_t track_place
);
void *open_cfw_retained_pdt_distortion_image_create(void *parent);
void open_cfw_retained_pdt_distortion_image_set_source(
    void *object, const void *source
);
void *open_cfw_retained_pdt_distortion_label_create(void *parent);
void open_cfw_retained_pdt_distortion_label_set_text(
    void *object, const char *text
);
uint32_t open_cfw_retained_pdt_distortion_translation_id(const char *key);
const char *open_cfw_retained_pdt_distortion_translation(
    const char *key, uint32_t id
);
void open_cfw_retained_pdt_distortion_set_text_color(
    void *object, open_cfw_pdt_distortion_color color, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_font(
    void *object, const void *font, uint32_t selector
);
void open_cfw_retained_pdt_distortion_set_text_align(
    void *object, uint32_t alignment, uint32_t selector
);

#ifndef OPEN_CFW_PDT_DISTORTION_ROOT
#define OPEN_CFW_PDT_DISTORTION_ROOT \
    (*(void * volatile *)(uintptr_t)0x2007487CU)
#endif
#ifndef OPEN_CFW_PDT_DISTORTION_REGISTRY_ROOT
#define OPEN_CFW_PDT_DISTORTION_REGISTRY_ROOT \
    (*(void * volatile *)(uintptr_t)0x20003068U)
#endif
#ifndef OPEN_CFW_PDT_DISTORTION_FONT
#define OPEN_CFW_PDT_DISTORTION_FONT \
    (*(const void * volatile *)(uintptr_t)0x200746DCU)
#endif
#ifndef OPEN_CFW_PDT_DISTORTION_IMAGE
#define OPEN_CFW_PDT_DISTORTION_IMAGE \
    ((const void *)(uintptr_t)0x00769F58U)
#endif
#ifndef OPEN_CFW_PDT_DISTORTION_TEXT_KEY_1
#define OPEN_CFW_PDT_DISTORTION_TEXT_KEY_1 \
    ((const char *)(uintptr_t)0x00736AF4U)
#endif
#ifndef OPEN_CFW_PDT_DISTORTION_TEXT_KEY_2
#define OPEN_CFW_PDT_DISTORTION_TEXT_KEY_2 \
    ((const char *)(uintptr_t)0x00736B24U)
#endif

#if defined(OPEN_CFW_PDT_DISTORTION_ZERO_STYLES_ONLY)
#define OPEN_CFW_PDT_DISTORTION_SELECTOR 1
#elif defined(OPEN_CFW_PDT_DISTORTION_COMMON_DATA_ONLY)
#define OPEN_CFW_PDT_DISTORTION_SELECTOR 2
#elif defined(OPEN_CFW_PDT_DISTORTION_PREDICATE_ONLY)
#define OPEN_CFW_PDT_DISTORTION_SELECTOR 3
#elif defined(OPEN_CFW_PDT_DISTORTION_SCREEN_EVENT_ONLY)
#define OPEN_CFW_PDT_DISTORTION_SELECTOR 4
#elif !defined(OPEN_CFW_PDT_DISTORTION_SELECTOR)
#define OPEN_CFW_PDT_DISTORTION_SELECTOR 0
#endif

#define OPEN_CFW_PDT_DISTORTION_BUILD(number) \
    (OPEN_CFW_PDT_DISTORTION_SELECTOR == 0 || \
     OPEN_CFW_PDT_DISTORTION_SELECTOR == (number))

#if defined(__arm__) || defined(__thumb__)
__asm__(
    ".type open_cfw_pdt_distortion_zero_styles,%function\n"
    ".type open_cfw_pdt_distortion_common_data_handler,%function\n"
    ".type open_cfw_pdt_distortion_predicate,%function\n"
    ".type open_cfw_pdt_distortion_screen_event,%function\n"
);
#endif

#if OPEN_CFW_PDT_DISTORTION_BUILD(1)
__attribute__((used, noinline))
void open_cfw_pdt_distortion_zero_styles(
    void *object, uint32_t value, uint32_t selector
)
{
    open_cfw_retained_pdt_distortion_set_style_0(object, value, selector);
    open_cfw_retained_pdt_distortion_set_style_1(object, value, selector);
    open_cfw_retained_pdt_distortion_set_style_2(object, value, selector);
    open_cfw_retained_pdt_distortion_set_style_3(object, value, selector);
}
#endif

#if OPEN_CFW_PDT_DISTORTION_BUILD(2)
__attribute__((used, noinline))
int open_cfw_pdt_distortion_common_data_handler(
    const void *context, const void *data, uint32_t length
)
{
    (void)context;
    (void)data;
    (void)length;
    return 0;
}
#endif

#if OPEN_CFW_PDT_DISTORTION_BUILD(3)
__attribute__((used, noinline))
int open_cfw_pdt_distortion_predicate(void)
{
    return 1;
}
#endif

#if OPEN_CFW_PDT_DISTORTION_BUILD(4)
static void open_cfw_pdt_distortion_clear_four_styles(void *object)
{
    open_cfw_retained_pdt_distortion_set_style_0(object, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_style_1(object, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_style_2(object, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_style_3(object, 0U, 0U);
}

static void open_cfw_pdt_distortion_set_translated_text(
    void *label, const char *key
)
{
    uint32_t id = open_cfw_retained_pdt_distortion_translation_id(key);
    const char *text = open_cfw_retained_pdt_distortion_translation(key, id);
    open_cfw_retained_pdt_distortion_label_set_text(label, text);
}

__attribute__((used, noinline))
int open_cfw_pdt_distortion_screen_event(
    uint32_t event, const void *argument_1, const void *argument_2,
    void *parent
)
{
    void *root;
    void *frame;
    void *column;
    void *row;
    void *image;
    void *label;
    open_cfw_pdt_distortion_color black;
    open_cfw_pdt_distortion_color white;

    (void)argument_1;
    (void)argument_2;
    if (event != OPEN_CFW_PDT_DISTORTION_CONSTRUCT_EVENT) {
        return 0;
    }

    black = open_cfw_retained_pdt_distortion_color_hex(0U);
    white = open_cfw_retained_pdt_distortion_color_hex(0xFFFFFFU);

    root = open_cfw_retained_pdt_distortion_object_create(parent);
    OPEN_CFW_PDT_DISTORTION_ROOT = root;
    open_cfw_retained_pdt_distortion_clear_flags(root, 0x10U);
    open_cfw_retained_pdt_distortion_set_width(root, 640);
    open_cfw_retained_pdt_distortion_set_height(root, 480);
    open_cfw_retained_pdt_distortion_set_bg_color(root, black, 0U);
    open_cfw_retained_pdt_distortion_set_bg_opacity(root, 255U, 0U);
    open_cfw_retained_pdt_distortion_set_border_width(root, 0, 0U);
    open_cfw_pdt_distortion_clear_four_styles(root);

    frame = open_cfw_retained_pdt_distortion_object_create(root);
    open_cfw_retained_pdt_distortion_clear_flags(frame, 0x10U);
    open_cfw_retained_pdt_distortion_set_pos(frame, 0, 50);
    open_cfw_retained_pdt_distortion_set_width(frame, 574);
    open_cfw_retained_pdt_distortion_set_height(frame, 206);
    open_cfw_retained_pdt_distortion_set_bg_color(frame, black, 0U);
    open_cfw_retained_pdt_distortion_set_bg_opacity(frame, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_border_width(frame, 2, 0U);
    open_cfw_retained_pdt_distortion_set_border_color(frame, white, 0U);
    open_cfw_retained_pdt_distortion_set_border_opacity(frame, 255U, 0U);
    open_cfw_retained_pdt_distortion_set_frame_style_0(frame, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_frame_style_1(frame, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_frame_style_2(frame, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_frame_style_3(frame, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_frame_style_4(frame, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_frame_style_5(frame, 0U, 0U);
    open_cfw_pdt_distortion_clear_four_styles(frame);
    open_cfw_pdt_distortion_clear_four_styles(frame);
    open_cfw_retained_pdt_distortion_set_scrollbar_mode(frame, 0U);
    open_cfw_retained_pdt_distortion_set_shadow_color(frame, white, 0U);
    open_cfw_retained_pdt_distortion_set_shadow_opacity(frame, 255U, 0U);

    column = open_cfw_retained_pdt_distortion_object_create(frame);
    open_cfw_retained_pdt_distortion_set_size(
        column, 0x3FFFFFFF, 0x3FFFFFFF
    );
    open_cfw_retained_pdt_distortion_set_bg_opacity(column, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_border_width(column, 0, 0U);
    open_cfw_pdt_distortion_clear_four_styles(column);
    open_cfw_retained_pdt_distortion_set_flex_flow(column, 1U);
    open_cfw_retained_pdt_distortion_set_flex_align(column, 2U, 2U, 2U);
    open_cfw_retained_pdt_distortion_set_layout_gap_0(column, 8U, 0U);
    open_cfw_retained_pdt_distortion_align(column, 9U, 0, 0);

    row = open_cfw_retained_pdt_distortion_object_create(column);
    open_cfw_retained_pdt_distortion_set_size(row, 0x3FFFFFFF, 0x3FFFFFFF);
    open_cfw_retained_pdt_distortion_set_bg_opacity(row, 0U, 0U);
    open_cfw_retained_pdt_distortion_set_border_width(row, 0, 0U);
    open_cfw_pdt_distortion_clear_four_styles(row);
    open_cfw_retained_pdt_distortion_set_flex_flow(row, 0U);
    open_cfw_retained_pdt_distortion_set_flex_align(row, 2U, 2U, 2U);
    open_cfw_retained_pdt_distortion_set_layout_gap_1(row, 8U, 0U);

    image = open_cfw_retained_pdt_distortion_image_create(row);
    open_cfw_retained_pdt_distortion_image_set_source(
        image, OPEN_CFW_PDT_DISTORTION_IMAGE
    );
    open_cfw_retained_pdt_distortion_set_width(image, 24);
    open_cfw_retained_pdt_distortion_set_height(image, 24);
    open_cfw_retained_pdt_distortion_add_flags(image, 0x10000U);
    open_cfw_retained_pdt_distortion_clear_flags(image, 0x10U);

    label = open_cfw_retained_pdt_distortion_label_create(row);
    open_cfw_retained_pdt_distortion_set_text_color(label, white, 0U);
    open_cfw_pdt_distortion_set_translated_text(
        label, OPEN_CFW_PDT_DISTORTION_TEXT_KEY_1
    );
    open_cfw_retained_pdt_distortion_set_font(
        label, OPEN_CFW_PDT_DISTORTION_FONT, 0U
    );

    label = open_cfw_retained_pdt_distortion_label_create(column);
    open_cfw_retained_pdt_distortion_set_text_color(label, white, 0U);
    open_cfw_pdt_distortion_set_translated_text(
        label, OPEN_CFW_PDT_DISTORTION_TEXT_KEY_2
    );
    open_cfw_retained_pdt_distortion_set_font(
        label, OPEN_CFW_PDT_DISTORTION_FONT, 0U
    );
    open_cfw_retained_pdt_distortion_set_text_align(label, 2U, 0U);

    OPEN_CFW_PDT_DISTORTION_REGISTRY_ROOT = root;
    return 0;
}
#endif
