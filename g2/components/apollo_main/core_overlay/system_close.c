/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the twenty linked functions in G2's
 * app/gui/SystemClose/systemClose.c object. EasyLogger calls are omitted as
 * non-controlling diagnostics; FIFO, page, selection, and lifecycle policy is
 * preserved.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_SYSTEM_CLOSE_APP_ID 0x22u
#define OPEN_CFW_SYSTEM_CLOSE_ROLE_MASTER 1u
#define OPEN_CFW_SYSTEM_CLOSE_ROLE_SLAVE 2u
#define OPEN_CFW_SYSTEM_CLOSE_STYLE_CONFIRMATION 1u
#define OPEN_CFW_SYSTEM_CLOSE_EVENT_CLICK 0x0au
#define OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_UP 0x44u
#define OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_DOWN 0x45u
#define OPEN_CFW_SYSTEM_CLOSE_EVENT_EXIT 0x48u
#define OPEN_CFW_SYSTEM_CLOSE_FIFO_CAPACITY 128u

struct open_cfw_system_close_fifo {
    uint8_t data[OPEN_CFW_SYSTEM_CLOSE_FIFO_CAPACITY];
    uint16_t write_index;
    uint16_t read_index;
    uint16_t count;
};

struct open_cfw_system_close_point {
    int32_t x;
    int32_t y;
};

struct open_cfw_system_close_page_event {
    uint8_t reserved[16];
    const struct open_cfw_system_close_point *point;
};

#ifndef OPEN_CFW_SYSTEM_CLOSE_FIFO
#define OPEN_CFW_SYSTEM_CLOSE_FIFO (*(volatile struct open_cfw_system_close_fifo *)(uintptr_t)0x20071840u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_ROOT
#define OPEN_CFW_SYSTEM_CLOSE_ROOT (*(volatile uintptr_t *)(uintptr_t)0x200749fcu)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_CONTENT
#define OPEN_CFW_SYSTEM_CLOSE_CONTENT (*(volatile uintptr_t *)(uintptr_t)0x20074a00u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_TIMESTAMP
#define OPEN_CFW_SYSTEM_CLOSE_TIMESTAMP (*(volatile uint32_t *)(uintptr_t)0x20074a04u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_ARROW
#define OPEN_CFW_SYSTEM_CLOSE_ARROW (*(volatile uintptr_t *)(uintptr_t)0x20074a08u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_NO_LABEL
#define OPEN_CFW_SYSTEM_CLOSE_NO_LABEL (*(volatile uintptr_t *)(uintptr_t)0x20074a0cu)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL
#define OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL (*(volatile uintptr_t *)(uintptr_t)0x20074a10u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_YES_LABEL
#define OPEN_CFW_SYSTEM_CLOSE_YES_LABEL (*(volatile uintptr_t *)(uintptr_t)0x20074a14u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SELECTED
#define OPEN_CFW_SYSTEM_CLOSE_SELECTED (*(volatile uint32_t *)(uintptr_t)0x20074a18u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL
#define OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL (*(volatile uintptr_t *)(uintptr_t)0x20074a1cu)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_STYLE
#define OPEN_CFW_SYSTEM_CLOSE_STYLE (*(volatile uint8_t *)(uintptr_t)0x20075026u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_VISIBLE
#define OPEN_CFW_SYSTEM_CLOSE_VISIBLE (*(volatile uint8_t *)(uintptr_t)0x20075027u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_ANIMATING
#define OPEN_CFW_SYSTEM_CLOSE_ANIMATING (*(volatile uint8_t *)(uintptr_t)0x20075028u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT
#define OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT (*(volatile uint32_t *)(uintptr_t)0x20003becu)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_PAGE_DESCRIPTOR
#define OPEN_CFW_SYSTEM_CLOSE_PAGE_DESCRIPTOR ((volatile uintptr_t *)(uintptr_t)0x20003bf0u)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_FONT
#define OPEN_CFW_SYSTEM_CLOSE_FONT (*(const void *volatile *)(uintptr_t)0x200746e0u)
#endif

#ifndef OPEN_CFW_SYSTEM_CLOSE_MEMSET
void *open_cfw_retained_system_close_memset(void *, int, size_t);
#define OPEN_CFW_SYSTEM_CLOSE_MEMSET(p,v,n) open_cfw_retained_system_close_memset((p),(v),(n))
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_OBJECT_CREATE
uintptr_t open_cfw_retained_system_close_object_create(uintptr_t);
#define OPEN_CFW_SYSTEM_CLOSE_OBJECT_CREATE(p) open_cfw_retained_system_close_object_create(p)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_SIZE
void open_cfw_retained_system_close_set_size(uintptr_t, int32_t, int32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_SIZE(...) open_cfw_retained_system_close_set_size(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_GET_WIDTH
int32_t open_cfw_retained_system_close_get_width(uintptr_t);
#define OPEN_CFW_SYSTEM_CLOSE_GET_WIDTH(o) open_cfw_retained_system_close_get_width(o)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_GET_HEIGHT
int32_t open_cfw_retained_system_close_get_height(uintptr_t);
#define OPEN_CFW_SYSTEM_CLOSE_GET_HEIGHT(o) open_cfw_retained_system_close_get_height(o)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_X
void open_cfw_retained_system_close_set_x(uintptr_t, int32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_X(...) open_cfw_retained_system_close_set_x(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_Y
void open_cfw_retained_system_close_set_y(uintptr_t, int32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_Y(...) open_cfw_retained_system_close_set_y(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_POS
void open_cfw_retained_system_close_set_pos(uintptr_t, int32_t, int32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_POS(...) open_cfw_retained_system_close_set_pos(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_CLEAR_FLAGS
void open_cfw_retained_system_close_clear_flags(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_CLEAR_FLAGS(...) open_cfw_retained_system_close_clear_flags(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_ADD_FLAGS
void open_cfw_retained_system_close_add_flags(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_ADD_FLAGS(...) open_cfw_retained_system_close_add_flags(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_LAYOUT
void open_cfw_retained_system_close_set_layout(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_LAYOUT(...) open_cfw_retained_system_close_set_layout(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_ALIGN
void open_cfw_retained_system_close_set_align(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_ALIGN(...) open_cfw_retained_system_close_set_align(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_COLOR
uint32_t open_cfw_retained_system_close_color(uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_COLOR(v) open_cfw_retained_system_close_color(v)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_BG_COLOR
void open_cfw_retained_system_close_set_bg_color(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_BG_COLOR(...) open_cfw_retained_system_close_set_bg_color(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_LABEL_BG_COLOR
void open_cfw_retained_system_close_set_label_bg_color(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_LABEL_BG_COLOR(...) open_cfw_retained_system_close_set_label_bg_color(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_BG_OPACITY
void open_cfw_retained_system_close_set_bg_opacity(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_BG_OPACITY(...) open_cfw_retained_system_close_set_bg_opacity(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_COLOR
void open_cfw_retained_system_close_set_text_color(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_COLOR(...) open_cfw_retained_system_close_set_text_color(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_ALIGN
void open_cfw_retained_system_close_set_text_align(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_ALIGN(...) open_cfw_retained_system_close_set_text_align(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_PAD_TOP
void open_cfw_retained_system_close_set_pad_top(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_PAD_TOP(...) open_cfw_retained_system_close_set_pad_top(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_PAD_BOTTOM
void open_cfw_retained_system_close_set_pad_bottom(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_PAD_BOTTOM(...) open_cfw_retained_system_close_set_pad_bottom(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_PAD_LEFT
void open_cfw_retained_system_close_set_pad_left(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_PAD_LEFT(...) open_cfw_retained_system_close_set_pad_left(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_PAD_RIGHT
void open_cfw_retained_system_close_set_pad_right(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_PAD_RIGHT(...) open_cfw_retained_system_close_set_pad_right(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_SCROLLBAR_MODE
void open_cfw_retained_system_close_set_scrollbar_mode(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_SCROLLBAR_MODE(...) open_cfw_retained_system_close_set_scrollbar_mode(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SET_FONT
void open_cfw_retained_system_close_set_font(uintptr_t, const void *, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SET_FONT(...) open_cfw_retained_system_close_set_font(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_DELETE_CHILDREN
void open_cfw_retained_system_close_delete_children(uintptr_t);
#define OPEN_CFW_SYSTEM_CLOSE_DELETE_CHILDREN(o) open_cfw_retained_system_close_delete_children(o)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_HIDE
void open_cfw_retained_system_close_hide(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_HIDE(...) open_cfw_retained_system_close_hide(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_IMAGE_CREATE
uintptr_t open_cfw_retained_system_close_image_create(uintptr_t);
#define OPEN_CFW_SYSTEM_CLOSE_IMAGE_CREATE(o) open_cfw_retained_system_close_image_create(o)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_IMAGE_SET_SOURCE
void open_cfw_retained_system_close_image_set_source(uintptr_t, const void *);
#define OPEN_CFW_SYSTEM_CLOSE_IMAGE_SET_SOURCE(...) open_cfw_retained_system_close_image_set_source(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_LABEL_CREATE
uintptr_t open_cfw_retained_system_close_label_create(uintptr_t);
#define OPEN_CFW_SYSTEM_CLOSE_LABEL_CREATE(o) open_cfw_retained_system_close_label_create(o)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_LABEL_SET_TEXT
void open_cfw_retained_system_close_label_set_text(uintptr_t, const char *);
#define OPEN_CFW_SYSTEM_CLOSE_LABEL_SET_TEXT(...) open_cfw_retained_system_close_label_set_text(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_TRANSLATION_ID
uint32_t open_cfw_retained_system_close_translation_id(const char *);
#define OPEN_CFW_SYSTEM_CLOSE_TRANSLATION_ID(s) open_cfw_retained_system_close_translation_id(s)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_TRANSLATION
const char *open_cfw_retained_system_close_translation(const char *, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_TRANSLATION(s,i) open_cfw_retained_system_close_translation((s),(i))
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_ROLE
uint32_t open_cfw_retained_system_close_role(void);
#define OPEN_CFW_SYSTEM_CLOSE_ROLE() open_cfw_retained_system_close_role()
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_DISPLAY_ACTIVE
uint32_t open_cfw_retained_system_close_display_active(void);
#define OPEN_CFW_SYSTEM_CLOSE_DISPLAY_ACTIVE() open_cfw_retained_system_close_display_active()
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_DISPLAY_STATE
uint32_t open_cfw_retained_system_close_display_state(uint32_t *, uint32_t *);
#define OPEN_CFW_SYSTEM_CLOSE_DISPLAY_STATE(...) open_cfw_retained_system_close_display_state(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_POST_SELF
uint32_t open_cfw_retained_system_close_post_self(uint32_t, const void *, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_POST_SELF(...) open_cfw_retained_system_close_post_self(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SEND_PAGE_ACTION
uint32_t open_cfw_retained_system_close_send_page_action(uint32_t, const void *, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SEND_PAGE_ACTION(...) open_cfw_retained_system_close_send_page_action(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_NOTIFY_STATE
uint32_t open_cfw_retained_system_close_notify_state(uint32_t, const void *, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_NOTIFY_STATE(...) open_cfw_retained_system_close_notify_state(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_SEND_FACTORY
uint32_t open_cfw_retained_system_close_send_factory(uint32_t, const void *, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_SEND_FACTORY(...) open_cfw_retained_system_close_send_factory(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_TRANSITION
uint32_t open_cfw_retained_system_close_transition(uint32_t, uint32_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_CLOSE_TRANSITION(...) open_cfw_retained_system_close_transition(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_ANIM_INIT
void open_cfw_retained_system_close_anim_init(void *);
#define OPEN_CFW_SYSTEM_CLOSE_ANIM_INIT(a) open_cfw_retained_system_close_anim_init(a)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_ANIM_SET_VALUES
void open_cfw_retained_system_close_anim_set_values(void *, int32_t, int32_t);
#define OPEN_CFW_SYSTEM_CLOSE_ANIM_SET_VALUES(...) open_cfw_retained_system_close_anim_set_values(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_CLOSE_ANIM_START
void open_cfw_retained_system_close_anim_start(void *);
#define OPEN_CFW_SYSTEM_CLOSE_ANIM_START(a) open_cfw_retained_system_close_anim_start(a)
#endif

#define OPEN_CFW_SYSTEM_CLOSE_ARROW_IMAGE ((const void *)(uintptr_t)0x0076a070u)
#define OPEN_CFW_SYSTEM_CLOSE_CONFIRM_ID ((const char *)(uintptr_t)0x00765bb0u)
#define OPEN_CFW_SYSTEM_CLOSE_NO_ID ((const char *)(uintptr_t)0x007896a0u)
#define OPEN_CFW_SYSTEM_CLOSE_YES_ID ((const char *)(uintptr_t)0x007896b0u)
#ifndef OPEN_CFW_SYSTEM_CLOSE_READY_CALLBACK
#define OPEN_CFW_SYSTEM_CLOSE_READY_CALLBACK open_cfw_system_close_selection_anim_ready
#endif

void open_cfw_system_close_set_box_padding(uintptr_t, uint32_t, uint32_t);
int32_t open_cfw_system_close_fifo_push(const uint8_t *, uint16_t);
uint32_t open_cfw_system_close_fifo_empty(void);
int32_t open_cfw_system_close_fifo_pop(uint8_t *, uint16_t);
void open_cfw_system_close_fifo_reset(void);
int32_t open_cfw_system_close_common_data_handler(uint32_t, const uint8_t *, uint32_t);
uint32_t open_cfw_system_close_dispatch_page_action(uint32_t, const void *);
uint32_t open_cfw_system_close_page_event_handler(uintptr_t, const void *, uint32_t, const void *);
void open_cfw_system_close_main_page_init(uintptr_t, const void *, uint32_t);
void open_cfw_system_close_option_position(void);
void open_cfw_system_close_selection_anim_ready(void);
void open_cfw_system_close_start_selection_animation(void);
void open_cfw_system_close_update_selection(void);
void open_cfw_system_close_handle_scroll_up(void);
void open_cfw_system_close_handle_scroll_down(void);
void open_cfw_system_close_handle_click(void);
void open_cfw_system_close_create_options(uint32_t);
void open_cfw_system_close_reflash_event_handler(const uint8_t *, uint32_t);
uint32_t open_cfw_system_close_page_factory(uint8_t, uint32_t);
uint32_t open_cfw_system_close_ui_event_handler(uint32_t, const void *, uint32_t, uintptr_t);

#if !defined(OPEN_CFW_SYSTEM_CLOSE_PADDING_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_FIFO_PUSH_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_FIFO_EMPTY_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_FIFO_POP_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_FIFO_RESET_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_COMMON_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_PAGE_ACTION_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_PAGE_EVENT_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_INIT_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_POSITION_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_ANIM_READY_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_ANIMATE_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_UPDATE_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_SCROLL_UP_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_SCROLL_DOWN_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_CLICK_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_OPTIONS_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_REFLASH_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_FACTORY_ONLY) && !defined(OPEN_CFW_SYSTEM_CLOSE_UI_EVENT_ONLY)
#define OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_PADDING_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_set_box_padding(uintptr_t object, uint32_t value, uint32_t selector)
{
    OPEN_CFW_SYSTEM_CLOSE_SET_PAD_TOP(object, value, selector);
    OPEN_CFW_SYSTEM_CLOSE_SET_PAD_BOTTOM(object, value, selector);
    OPEN_CFW_SYSTEM_CLOSE_SET_PAD_LEFT(object, value, selector);
    OPEN_CFW_SYSTEM_CLOSE_SET_PAD_RIGHT(object, value, selector);
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_FIFO_PUSH_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_system_close_fifo_push(const uint8_t *data, uint16_t length)
{
    uint16_t index;
    if (data == NULL || length == 0u) return -3;
    if (length > OPEN_CFW_SYSTEM_CLOSE_FIFO_CAPACITY - OPEN_CFW_SYSTEM_CLOSE_FIFO.count) return -1;
    for (index = 0u; index < length; ++index) {
        OPEN_CFW_SYSTEM_CLOSE_FIFO.data[OPEN_CFW_SYSTEM_CLOSE_FIFO.write_index] = data[index];
        OPEN_CFW_SYSTEM_CLOSE_FIFO.write_index = (uint16_t)((OPEN_CFW_SYSTEM_CLOSE_FIFO.write_index + 1u) % OPEN_CFW_SYSTEM_CLOSE_FIFO_CAPACITY);
        ++OPEN_CFW_SYSTEM_CLOSE_FIFO.count;
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_FIFO_EMPTY_ONLY)
__attribute__((used, noinline)) uint32_t open_cfw_system_close_fifo_empty(void)
{
    return OPEN_CFW_SYSTEM_CLOSE_FIFO.count == 0u;
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_FIFO_POP_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_system_close_fifo_pop(uint8_t *data, uint16_t length)
{
    uint16_t index;
    if (data == NULL || length == 0u) return -3;
    if (OPEN_CFW_SYSTEM_CLOSE_FIFO.count == 0u) return 0;
    if (length > OPEN_CFW_SYSTEM_CLOSE_FIFO.count) length = OPEN_CFW_SYSTEM_CLOSE_FIFO.count;
    for (index = 0u; index < length; ++index) {
        data[index] = OPEN_CFW_SYSTEM_CLOSE_FIFO.data[OPEN_CFW_SYSTEM_CLOSE_FIFO.read_index];
        OPEN_CFW_SYSTEM_CLOSE_FIFO.read_index = (uint16_t)((OPEN_CFW_SYSTEM_CLOSE_FIFO.read_index + 1u) % OPEN_CFW_SYSTEM_CLOSE_FIFO_CAPACITY);
        --OPEN_CFW_SYSTEM_CLOSE_FIFO.count;
    }
    return (int32_t)length;
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_FIFO_RESET_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_fifo_reset(void)
{
    OPEN_CFW_SYSTEM_CLOSE_FIFO.write_index = 0u;
    OPEN_CFW_SYSTEM_CLOSE_FIFO.read_index = 0u;
    OPEN_CFW_SYSTEM_CLOSE_FIFO.count = 0u;
    (void)OPEN_CFW_SYSTEM_CLOSE_MEMSET((void *)(uintptr_t)&OPEN_CFW_SYSTEM_CLOSE_FIFO.data[0], 0, OPEN_CFW_SYSTEM_CLOSE_FIFO_CAPACITY);
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_COMMON_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_system_close_common_data_handler(uint32_t event, const uint8_t *data, uint32_t length)
{
    uint32_t active_app = 0u;
    uint32_t display_state = 0u;
    (void)event;
    if (data == NULL || length != 5u) return -1;
    OPEN_CFW_SYSTEM_CLOSE_STYLE = data[0];
    OPEN_CFW_SYSTEM_CLOSE_TIMESTAMP = (uint32_t)data[1] | ((uint32_t)data[2] << 8) | ((uint32_t)data[3] << 16) | ((uint32_t)data[4] << 24);
    if (OPEN_CFW_SYSTEM_CLOSE_ROLE() != OPEN_CFW_SYSTEM_CLOSE_ROLE_MASTER || OPEN_CFW_SYSTEM_CLOSE_DISPLAY_ACTIVE() != 1u) return 0;
    (void)OPEN_CFW_SYSTEM_CLOSE_DISPLAY_STATE(&active_app, &display_state);
    if (display_state == 0u && (active_app == 8u || active_app == 11u || active_app == 5u || active_app == 6u || active_app == 0xe0u || active_app == 0xffeu)) {
        (void)OPEN_CFW_SYSTEM_CLOSE_POST_SELF(OPEN_CFW_SYSTEM_CLOSE_APP_ID, NULL, 0u, 100u);
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_PAGE_ACTION_ONLY)
__attribute__((used, noinline)) uint32_t open_cfw_system_close_dispatch_page_action(uint32_t event, const void *context)
{
    uint8_t packet[6] = {0u, (uint8_t)event, 0u, 0u, 0u, 0u};
    if (OPEN_CFW_SYSTEM_CLOSE_ANIMATING != 0u) return 0u;
    if ((event == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_UP || event == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_DOWN) && context != NULL) {
        const struct open_cfw_system_close_page_event *page_event = (const struct open_cfw_system_close_page_event *)context;
        if (page_event->point != NULL) {
            packet[2] = (uint8_t)page_event->point->x;
            packet[3] = (uint8_t)((uint32_t)page_event->point->x >> 8);
            packet[4] = (uint8_t)page_event->point->y;
            packet[5] = (uint8_t)((uint32_t)page_event->point->y >> 8);
        }
    }
    if (event == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_UP || event == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_DOWN || event == 0x4au || event == OPEN_CFW_SYSTEM_CLOSE_EVENT_CLICK || event == OPEN_CFW_SYSTEM_CLOSE_EVENT_EXIT || event == 0x49u) {
        return OPEN_CFW_SYSTEM_CLOSE_SEND_PAGE_ACTION(OPEN_CFW_SYSTEM_CLOSE_APP_ID, packet, sizeof(packet), 0u);
    }
    return 0u;
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_PAGE_EVENT_ONLY)
__attribute__((used, noinline)) uint32_t open_cfw_system_close_page_event_handler(uintptr_t object, const void *data, uint32_t event, const void *context)
{
    (void)object; (void)data;
    if (event == OPEN_CFW_SYSTEM_CLOSE_EVENT_CLICK) {
        if (OPEN_CFW_SYSTEM_CLOSE_ROLE() == OPEN_CFW_SYSTEM_CLOSE_ROLE_MASTER) open_cfw_system_close_handle_click();
    } else if (event == OPEN_CFW_SYSTEM_CLOSE_EVENT_EXIT || event == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_UP || event == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_DOWN) {
        if (OPEN_CFW_SYSTEM_CLOSE_ROLE() != OPEN_CFW_SYSTEM_CLOSE_ROLE_SLAVE) (void)open_cfw_system_close_dispatch_page_action(event, context);
    }
    return 1u;
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_INIT_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_main_page_init(uintptr_t parent, const void *data, uint32_t length)
{
    int32_t parent_width;
    int32_t parent_height;
    (void)data; (void)length;
    OPEN_CFW_SYSTEM_CLOSE_ROOT = OPEN_CFW_SYSTEM_CLOSE_OBJECT_CREATE(parent);
    OPEN_CFW_SYSTEM_CLOSE_SET_SIZE(OPEN_CFW_SYSTEM_CLOSE_ROOT, 200, 40);
    parent_width = OPEN_CFW_SYSTEM_CLOSE_GET_WIDTH(parent);
    parent_height = OPEN_CFW_SYSTEM_CLOSE_GET_HEIGHT(parent);
    OPEN_CFW_SYSTEM_CLOSE_SET_X(OPEN_CFW_SYSTEM_CLOSE_ROOT, (parent_width - 200) / 2);
    OPEN_CFW_SYSTEM_CLOSE_SET_Y(OPEN_CFW_SYSTEM_CLOSE_ROOT, (parent_height - 40) / 2);
    OPEN_CFW_SYSTEM_CLOSE_CLEAR_FLAGS(OPEN_CFW_SYSTEM_CLOSE_ROOT, 0x2004u);
    OPEN_CFW_SYSTEM_CLOSE_SET_LAYOUT(OPEN_CFW_SYSTEM_CLOSE_ROOT, 0u);
    OPEN_CFW_SYSTEM_CLOSE_SET_BG_COLOR(OPEN_CFW_SYSTEM_CLOSE_ROOT, OPEN_CFW_SYSTEM_CLOSE_COLOR(0u), 0u);
    OPEN_CFW_SYSTEM_CLOSE_SET_BG_OPACITY(OPEN_CFW_SYSTEM_CLOSE_ROOT, 0xffu, 0u);
    OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_COLOR(OPEN_CFW_SYSTEM_CLOSE_ROOT, OPEN_CFW_SYSTEM_CLOSE_COLOR(0u), 0u);
    OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_ALIGN(OPEN_CFW_SYSTEM_CLOSE_ROOT, 0u, 0u);
    open_cfw_system_close_set_box_padding(OPEN_CFW_SYSTEM_CLOSE_ROOT, 0u, 0u);
    OPEN_CFW_SYSTEM_CLOSE_CONTENT = OPEN_CFW_SYSTEM_CLOSE_OBJECT_CREATE(OPEN_CFW_SYSTEM_CLOSE_ROOT);
    OPEN_CFW_SYSTEM_CLOSE_SET_SIZE(OPEN_CFW_SYSTEM_CLOSE_CONTENT, 184, 40);
    OPEN_CFW_SYSTEM_CLOSE_SET_X(OPEN_CFW_SYSTEM_CLOSE_CONTENT, OPEN_CFW_SYSTEM_CLOSE_ROLE() == OPEN_CFW_SYSTEM_CLOSE_ROLE_MASTER ? 0 : 16);
    OPEN_CFW_SYSTEM_CLOSE_SET_Y(OPEN_CFW_SYSTEM_CLOSE_CONTENT, 0);
    OPEN_CFW_SYSTEM_CLOSE_SET_LAYOUT(OPEN_CFW_SYSTEM_CLOSE_CONTENT, 0u);
    OPEN_CFW_SYSTEM_CLOSE_SET_ALIGN(OPEN_CFW_SYSTEM_CLOSE_CONTENT, 12u);
    OPEN_CFW_SYSTEM_CLOSE_SET_BG_OPACITY(OPEN_CFW_SYSTEM_CLOSE_CONTENT, 0u, 0u);
    OPEN_CFW_SYSTEM_CLOSE_SET_SCROLLBAR_MODE(OPEN_CFW_SYSTEM_CLOSE_CONTENT, 10u);
    OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_COLOR(OPEN_CFW_SYSTEM_CLOSE_CONTENT, OPEN_CFW_SYSTEM_CLOSE_COLOR(0xffffffu), 0u);
    OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_ALIGN(OPEN_CFW_SYSTEM_CLOSE_CONTENT, 1u, 0u);
    open_cfw_system_close_set_box_padding(OPEN_CFW_SYSTEM_CLOSE_CONTENT, 0u, 0u);
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_POSITION_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_option_position(void)
{
    if (OPEN_CFW_SYSTEM_CLOSE_ARROW == 0u || OPEN_CFW_SYSTEM_CLOSE_NO_LABEL == 0u || OPEN_CFW_SYSTEM_CLOSE_YES_LABEL == 0u) return;
    OPEN_CFW_SYSTEM_CLOSE_SET_X(OPEN_CFW_SYSTEM_CLOSE_NO_LABEL, 8);
    OPEN_CFW_SYSTEM_CLOSE_SET_X(OPEN_CFW_SYSTEM_CLOSE_YES_LABEL, 96);
    if (OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT == 3u && OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL != 0u) OPEN_CFW_SYSTEM_CLOSE_SET_X(OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL, 52);
    open_cfw_system_close_update_selection();
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_ANIM_READY_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_selection_anim_ready(void)
{
    uint8_t packet[5] = {0u, 0u, 0u, 0u, 0u};
    OPEN_CFW_SYSTEM_CLOSE_ANIMATING = 0u;
    if (open_cfw_system_close_fifo_empty() != 0u) return;
    (void)open_cfw_system_close_fifo_pop(packet, sizeof(packet));
    if (packet[0] == OPEN_CFW_SYSTEM_CLOSE_EVENT_CLICK) open_cfw_system_close_handle_click();
    else if (packet[0] == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_UP) open_cfw_system_close_handle_scroll_up();
    else if (packet[0] == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_DOWN) open_cfw_system_close_handle_scroll_down();
    else if (packet[0] == OPEN_CFW_SYSTEM_CLOSE_EVENT_EXIT && OPEN_CFW_SYSTEM_CLOSE_ROLE() == OPEN_CFW_SYSTEM_CLOSE_ROLE_MASTER) (void)OPEN_CFW_SYSTEM_CLOSE_NOTIFY_STATE(OPEN_CFW_SYSTEM_CLOSE_APP_ID, NULL, 0u, 0u);
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_ANIMATE_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_start_selection_animation(void)
{
    uint32_t animation[24];
    OPEN_CFW_SYSTEM_CLOSE_ANIM_INIT(animation);
    animation[0] = (uint32_t)OPEN_CFW_SYSTEM_CLOSE_ROOT;
    animation[1] = 0x0046a3d7u;
    OPEN_CFW_SYSTEM_CLOSE_ANIM_SET_VALUES(animation, 0, 0);
    animation[12] = 200u;
    animation[8] = 0x00450635u;
    animation[4] = (uint32_t)(uintptr_t)OPEN_CFW_SYSTEM_CLOSE_READY_CALLBACK;
    OPEN_CFW_SYSTEM_CLOSE_ANIMATING = 1u;
    OPEN_CFW_SYSTEM_CLOSE_ANIM_START(animation);
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_UPDATE_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_update_selection(void)
{
    uintptr_t selected = 0u;
    uint32_t index = OPEN_CFW_SYSTEM_CLOSE_SELECTED;
    if (OPEN_CFW_SYSTEM_CLOSE_ARROW == 0u) return;
    if (index == 0u) selected = OPEN_CFW_SYSTEM_CLOSE_NO_LABEL;
    else if (index == 1u) selected = OPEN_CFW_SYSTEM_CLOSE_YES_LABEL;
    else if (index == 2u && OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT == 3u) selected = OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL;
    if (selected != 0u) OPEN_CFW_SYSTEM_CLOSE_SET_POS(OPEN_CFW_SYSTEM_CLOSE_ARROW, (int32_t)(index * 44u), 0);
    if (OPEN_CFW_SYSTEM_CLOSE_NO_LABEL != 0u) OPEN_CFW_SYSTEM_CLOSE_SET_LABEL_BG_COLOR(OPEN_CFW_SYSTEM_CLOSE_NO_LABEL, OPEN_CFW_SYSTEM_CLOSE_COLOR(index == 0u ? 0xffffffu : 0x00444444u), 0u);
    if (OPEN_CFW_SYSTEM_CLOSE_YES_LABEL != 0u) OPEN_CFW_SYSTEM_CLOSE_SET_LABEL_BG_COLOR(OPEN_CFW_SYSTEM_CLOSE_YES_LABEL, OPEN_CFW_SYSTEM_CLOSE_COLOR(index == 1u ? 0xffffffu : 0x00444444u), 0u);
    if (OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL != 0u && OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT == 3u) OPEN_CFW_SYSTEM_CLOSE_SET_LABEL_BG_COLOR(OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL, OPEN_CFW_SYSTEM_CLOSE_COLOR(index == 2u ? 0xffffffu : 0x00444444u), 0u);
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_SCROLL_UP_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_handle_scroll_up(void)
{
    if (OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT == 0u || OPEN_CFW_SYSTEM_CLOSE_SELECTED + 1u >= OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT) return;
    ++OPEN_CFW_SYSTEM_CLOSE_SELECTED;
    open_cfw_system_close_update_selection();
    open_cfw_system_close_start_selection_animation();
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_SCROLL_DOWN_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_handle_scroll_down(void)
{
    if (OPEN_CFW_SYSTEM_CLOSE_SELECTED == 0u) return;
    --OPEN_CFW_SYSTEM_CLOSE_SELECTED;
    open_cfw_system_close_update_selection();
    open_cfw_system_close_start_selection_animation();
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_CLICK_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_handle_click(void)
{
    uint32_t confirm = (OPEN_CFW_SYSTEM_CLOSE_STYLE == 2u && OPEN_CFW_SYSTEM_CLOSE_SELECTED == 1u) || (OPEN_CFW_SYSTEM_CLOSE_STYLE == 3u && OPEN_CFW_SYSTEM_CLOSE_SELECTED == 2u);
    uint32_t cancel = OPEN_CFW_SYSTEM_CLOSE_SELECTED == 0u;
    if (OPEN_CFW_SYSTEM_CLOSE_ROLE() != OPEN_CFW_SYSTEM_CLOSE_ROLE_MASTER) return;
    if (cancel || confirm) (void)OPEN_CFW_SYSTEM_CLOSE_NOTIFY_STATE(OPEN_CFW_SYSTEM_CLOSE_APP_ID, NULL, 0u, 0u);
    if (confirm) (void)OPEN_CFW_SYSTEM_CLOSE_TRANSITION(6u, 15u, 0u, 500u);
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_OPTIONS_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_create_options(uint32_t style)
{
    OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT = style == OPEN_CFW_SYSTEM_CLOSE_STYLE_CONFIRMATION ? 2u : 3u;
    OPEN_CFW_SYSTEM_CLOSE_ARROW = OPEN_CFW_SYSTEM_CLOSE_IMAGE_CREATE(OPEN_CFW_SYSTEM_CLOSE_CONTENT);
    OPEN_CFW_SYSTEM_CLOSE_IMAGE_SET_SOURCE(OPEN_CFW_SYSTEM_CLOSE_ARROW, OPEN_CFW_SYSTEM_CLOSE_ARROW_IMAGE);
    OPEN_CFW_SYSTEM_CLOSE_SET_SIZE(OPEN_CFW_SYSTEM_CLOSE_ARROW, 18, 18);
    if (style == OPEN_CFW_SYSTEM_CLOSE_STYLE_CONFIRMATION) {
        OPEN_CFW_SYSTEM_CLOSE_NO_LABEL = OPEN_CFW_SYSTEM_CLOSE_LABEL_CREATE(OPEN_CFW_SYSTEM_CLOSE_CONTENT);
        OPEN_CFW_SYSTEM_CLOSE_LABEL_SET_TEXT(OPEN_CFW_SYSTEM_CLOSE_NO_LABEL, OPEN_CFW_SYSTEM_CLOSE_TRANSLATION(OPEN_CFW_SYSTEM_CLOSE_NO_ID, OPEN_CFW_SYSTEM_CLOSE_TRANSLATION_ID(OPEN_CFW_SYSTEM_CLOSE_NO_ID)));
        OPEN_CFW_SYSTEM_CLOSE_SET_FONT(OPEN_CFW_SYSTEM_CLOSE_NO_LABEL, OPEN_CFW_SYSTEM_CLOSE_FONT, 0u);
        OPEN_CFW_SYSTEM_CLOSE_SET_SIZE(OPEN_CFW_SYSTEM_CLOSE_NO_LABEL, 0x3fffffff, 0x3fffffff);
        OPEN_CFW_SYSTEM_CLOSE_ADD_FLAGS(OPEN_CFW_SYSTEM_CLOSE_NO_LABEL, 0x10000u);
        OPEN_CFW_SYSTEM_CLOSE_CLEAR_FLAGS(OPEN_CFW_SYSTEM_CLOSE_NO_LABEL, 16u);
        OPEN_CFW_SYSTEM_CLOSE_SET_LABEL_BG_COLOR(OPEN_CFW_SYSTEM_CLOSE_NO_LABEL, OPEN_CFW_SYSTEM_CLOSE_COLOR(0xffffffu), 0u);
        OPEN_CFW_SYSTEM_CLOSE_YES_LABEL = OPEN_CFW_SYSTEM_CLOSE_LABEL_CREATE(OPEN_CFW_SYSTEM_CLOSE_CONTENT);
        OPEN_CFW_SYSTEM_CLOSE_LABEL_SET_TEXT(OPEN_CFW_SYSTEM_CLOSE_YES_LABEL, OPEN_CFW_SYSTEM_CLOSE_TRANSLATION(OPEN_CFW_SYSTEM_CLOSE_YES_ID, OPEN_CFW_SYSTEM_CLOSE_TRANSLATION_ID(OPEN_CFW_SYSTEM_CLOSE_YES_ID)));
        OPEN_CFW_SYSTEM_CLOSE_SET_FONT(OPEN_CFW_SYSTEM_CLOSE_YES_LABEL, OPEN_CFW_SYSTEM_CLOSE_FONT, 0u);
        OPEN_CFW_SYSTEM_CLOSE_SET_SIZE(OPEN_CFW_SYSTEM_CLOSE_YES_LABEL, 0x3fffffff, 0x3fffffff);
        OPEN_CFW_SYSTEM_CLOSE_ADD_FLAGS(OPEN_CFW_SYSTEM_CLOSE_YES_LABEL, 0x10000u);
        OPEN_CFW_SYSTEM_CLOSE_CLEAR_FLAGS(OPEN_CFW_SYSTEM_CLOSE_YES_LABEL, 16u);
        OPEN_CFW_SYSTEM_CLOSE_SET_LABEL_BG_COLOR(OPEN_CFW_SYSTEM_CLOSE_YES_LABEL, OPEN_CFW_SYSTEM_CLOSE_COLOR(0xffffffu), 0u);
    }
    OPEN_CFW_SYSTEM_CLOSE_SELECTED = 0u;
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_REFLASH_ONLY)
__attribute__((used, noinline)) void open_cfw_system_close_reflash_event_handler(const uint8_t *data, uint32_t length)
{
    uint8_t event;
    if (data == NULL || length == 0u) {
        if (OPEN_CFW_SYSTEM_CLOSE_STYLE == OPEN_CFW_SYSTEM_CLOSE_STYLE_CONFIRMATION) {
            OPEN_CFW_SYSTEM_CLOSE_DELETE_CHILDREN(OPEN_CFW_SYSTEM_CLOSE_CONTENT);
            OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL = OPEN_CFW_SYSTEM_CLOSE_LABEL_CREATE(OPEN_CFW_SYSTEM_CLOSE_CONTENT);
            OPEN_CFW_SYSTEM_CLOSE_LABEL_SET_TEXT(OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL, OPEN_CFW_SYSTEM_CLOSE_TRANSLATION(OPEN_CFW_SYSTEM_CLOSE_CONFIRM_ID, OPEN_CFW_SYSTEM_CLOSE_TRANSLATION_ID(OPEN_CFW_SYSTEM_CLOSE_CONFIRM_ID)));
            OPEN_CFW_SYSTEM_CLOSE_SET_SIZE(OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL, 0x3fffffff, 0x3fffffff);
            OPEN_CFW_SYSTEM_CLOSE_ADD_FLAGS(OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL, 0x10000u);
            OPEN_CFW_SYSTEM_CLOSE_CLEAR_FLAGS(OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL, 16u);
            OPEN_CFW_SYSTEM_CLOSE_SET_FONT(OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL, OPEN_CFW_SYSTEM_CLOSE_FONT, 0u);
            OPEN_CFW_SYSTEM_CLOSE_SET_LABEL_BG_COLOR(OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL, OPEN_CFW_SYSTEM_CLOSE_COLOR(0xffffffu), 0u);
            open_cfw_system_close_create_options(OPEN_CFW_SYSTEM_CLOSE_STYLE_CONFIRMATION);
            open_cfw_system_close_option_position();
            OPEN_CFW_SYSTEM_CLOSE_VISIBLE = 1u;
        }
        return;
    }
    if (length < 2u || data[0] != 0u) return;
    event = data[1];
    if (OPEN_CFW_SYSTEM_CLOSE_ANIMATING != 0u) {
        if (length >= 6u) (void)open_cfw_system_close_fifo_push(data + 1, 5u);
        return;
    }
    if (event == OPEN_CFW_SYSTEM_CLOSE_EVENT_CLICK) open_cfw_system_close_handle_click();
    else if (event == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_UP) open_cfw_system_close_handle_scroll_up();
    else if (event == OPEN_CFW_SYSTEM_CLOSE_EVENT_SCROLL_DOWN) open_cfw_system_close_handle_scroll_down();
    else if (event == OPEN_CFW_SYSTEM_CLOSE_EVENT_EXIT && OPEN_CFW_SYSTEM_CLOSE_ROLE() == OPEN_CFW_SYSTEM_CLOSE_ROLE_MASTER) (void)OPEN_CFW_SYSTEM_CLOSE_NOTIFY_STATE(OPEN_CFW_SYSTEM_CLOSE_APP_ID, NULL, 0u, 0u);
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_FACTORY_ONLY)
__attribute__((used, noinline)) uint32_t open_cfw_system_close_page_factory(uint8_t type, uint32_t value)
{
    uint8_t packet[5];
    packet[0] = type;
    packet[1] = (uint8_t)value;
    packet[2] = (uint8_t)(value >> 8);
    packet[3] = (uint8_t)(value >> 16);
    packet[4] = (uint8_t)(value >> 24);
    return OPEN_CFW_SYSTEM_CLOSE_SEND_FACTORY(OPEN_CFW_SYSTEM_CLOSE_APP_ID, packet, sizeof(packet), 0u);
}
#endif

#if defined(OPEN_CFW_SYSTEM_CLOSE_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_CLOSE_UI_EVENT_ONLY)
__attribute__((used, noinline)) uint32_t open_cfw_system_close_ui_event_handler(uint32_t type, const void *data, uint32_t length, uintptr_t parent)
{
    if (type == 2u) {
        OPEN_CFW_SYSTEM_CLOSE_ANIMATING = 0u;
        open_cfw_system_close_fifo_reset();
        OPEN_CFW_SYSTEM_CLOSE_SELECTED = 0u;
        OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT = 2u;
        OPEN_CFW_SYSTEM_CLOSE_ARROW = 0u;
        OPEN_CFW_SYSTEM_CLOSE_NO_LABEL = 0u;
        OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL = 0u;
        OPEN_CFW_SYSTEM_CLOSE_YES_LABEL = 0u;
        open_cfw_system_close_main_page_init(parent, data, length);
        OPEN_CFW_SYSTEM_CLOSE_PAGE_DESCRIPTOR[1] = OPEN_CFW_SYSTEM_CLOSE_ROOT;
    } else if (type == 3u) {
        open_cfw_system_close_reflash_event_handler((const uint8_t *)data, length);
    } else if (type == 5u) {
        OPEN_CFW_SYSTEM_CLOSE_ANIMATING = 0u;
        if (OPEN_CFW_SYSTEM_CLOSE_ROOT != 0u) OPEN_CFW_SYSTEM_CLOSE_HIDE(OPEN_CFW_SYSTEM_CLOSE_ROOT, 0u);
        open_cfw_system_close_fifo_reset();
        OPEN_CFW_SYSTEM_CLOSE_SELECTED = 0u;
        OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT = 2u;
        OPEN_CFW_SYSTEM_CLOSE_ARROW = 0u;
        OPEN_CFW_SYSTEM_CLOSE_NO_LABEL = 0u;
        OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL = 0u;
        OPEN_CFW_SYSTEM_CLOSE_YES_LABEL = 0u;
    }
    return 0u;
}
#endif
