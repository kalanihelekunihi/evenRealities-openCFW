/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room reconstruction of the seven linked functions in G2's
 * app/gui/SystemAlert/systemAlert.c object.  EasyLogger calls are omitted as
 * non-controlling diagnostics; UI, role, timing, and event behavior is kept.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_SYSTEM_ALERT_APP_ID 0x21u
#define OPEN_CFW_SYSTEM_ALERT_ROLE_MASTER 1u
#define OPEN_CFW_SYSTEM_ALERT_ROLE_SLAVE 2u
#define OPEN_CFW_SYSTEM_ALERT_DURATION 180u
#define OPEN_CFW_SYSTEM_ALERT_EXIT_EVENT 5u
#define OPEN_CFW_SYSTEM_ALERT_THROTTLE_TICKS 10000u

#ifndef OPEN_CFW_SYSTEM_ALERT_TYPE
#define OPEN_CFW_SYSTEM_ALERT_TYPE (*(volatile uint8_t *)(uintptr_t)0x200749f4u)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_ROOT
#define OPEN_CFW_SYSTEM_ALERT_ROOT (*(volatile uintptr_t *)(uintptr_t)0x200749ecu)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_CONTENT
#define OPEN_CFW_SYSTEM_ALERT_CONTENT (*(volatile uintptr_t *)(uintptr_t)0x200749f0u)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_LAST_TICK
#define OPEN_CFW_SYSTEM_ALERT_LAST_TICK (*(volatile uint32_t *)(uintptr_t)0x200749f8u)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_VISIBLE
#define OPEN_CFW_SYSTEM_ALERT_VISIBLE (*(volatile uint8_t *)(uintptr_t)0x20075025u)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_ANIMATION_TICKS
#define OPEN_CFW_SYSTEM_ALERT_ANIMATION_TICKS (*(volatile uint32_t *)(uintptr_t)0x20003bccu)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_PAGE_DESCRIPTOR
#define OPEN_CFW_SYSTEM_ALERT_PAGE_DESCRIPTOR ((volatile uintptr_t *)(uintptr_t)0x20003bd0u)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_FONT
#define OPEN_CFW_SYSTEM_ALERT_FONT (*(const void *volatile *)(uintptr_t)0x200746e0u)
#endif

#ifndef OPEN_CFW_SYSTEM_ALERT_OBJECT_CREATE
uintptr_t open_cfw_retained_system_alert_object_create(uintptr_t);
#define OPEN_CFW_SYSTEM_ALERT_OBJECT_CREATE(parent) open_cfw_retained_system_alert_object_create(parent)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_WIDTH
void open_cfw_retained_system_alert_set_width(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_WIDTH(o,v) open_cfw_retained_system_alert_set_width((o),(v))
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_HEIGHT
void open_cfw_retained_system_alert_set_height(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_HEIGHT(o,v) open_cfw_retained_system_alert_set_height((o),(v))
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_FLEX_FLOW
void open_cfw_retained_system_alert_set_flex_flow(uintptr_t, uint32_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_FLEX_FLOW(...) open_cfw_retained_system_alert_set_flex_flow(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_ADD_FLAGS
void open_cfw_retained_system_alert_add_flags(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_ADD_FLAGS(o,v) open_cfw_retained_system_alert_add_flags((o),(v))
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_CLEAR_FLAGS
void open_cfw_retained_system_alert_clear_flags(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_CLEAR_FLAGS(o,v) open_cfw_retained_system_alert_clear_flags((o),(v))
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_LAYOUT
void open_cfw_retained_system_alert_set_layout(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_LAYOUT(o,v) open_cfw_retained_system_alert_set_layout((o),(v))
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_ALIGN
void open_cfw_retained_system_alert_set_align(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_ALIGN(o,v) open_cfw_retained_system_alert_set_align((o),(v))
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_COLOR
uint32_t open_cfw_retained_system_alert_color(uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_COLOR(v) open_cfw_retained_system_alert_color(v)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_BG_COLOR
void open_cfw_retained_system_alert_set_bg_color(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_BG_COLOR(...) open_cfw_retained_system_alert_set_bg_color(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_LABEL_BG_COLOR
void open_cfw_retained_system_alert_set_label_bg_color(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_LABEL_BG_COLOR(...) open_cfw_retained_system_alert_set_label_bg_color(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_BG_OPACITY
void open_cfw_retained_system_alert_set_bg_opacity(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_BG_OPACITY(...) open_cfw_retained_system_alert_set_bg_opacity(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_TEXT_COLOR
void open_cfw_retained_system_alert_set_text_color(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_TEXT_COLOR(...) open_cfw_retained_system_alert_set_text_color(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_TEXT_ALIGN
void open_cfw_retained_system_alert_set_text_align(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_TEXT_ALIGN(...) open_cfw_retained_system_alert_set_text_align(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_PAD_TOP
void open_cfw_retained_system_alert_set_pad_top(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_PAD_TOP(...) open_cfw_retained_system_alert_set_pad_top(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_PAD_BOTTOM
void open_cfw_retained_system_alert_set_pad_bottom(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_PAD_BOTTOM(...) open_cfw_retained_system_alert_set_pad_bottom(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_PAD_LEFT
void open_cfw_retained_system_alert_set_pad_left(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_PAD_LEFT(...) open_cfw_retained_system_alert_set_pad_left(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_PAD_RIGHT
void open_cfw_retained_system_alert_set_pad_right(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_PAD_RIGHT(...) open_cfw_retained_system_alert_set_pad_right(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_RADIUS
void open_cfw_retained_system_alert_set_radius(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_RADIUS(...) open_cfw_retained_system_alert_set_radius(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_BORDER_WIDTH
void open_cfw_retained_system_alert_set_border_width(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_BORDER_WIDTH(...) open_cfw_retained_system_alert_set_border_width(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_SCROLLBAR_MODE
void open_cfw_retained_system_alert_set_scrollbar_mode(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_SCROLLBAR_MODE(o,v) open_cfw_retained_system_alert_set_scrollbar_mode((o),(v))
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_SCROLL_DIR
void open_cfw_retained_system_alert_set_scroll_dir(uintptr_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_SCROLL_DIR(o,v) open_cfw_retained_system_alert_set_scroll_dir((o),(v))
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SET_FONT
void open_cfw_retained_system_alert_set_font(uintptr_t, const void *, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SET_FONT(...) open_cfw_retained_system_alert_set_font(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_DELETE_CHILDREN
void open_cfw_retained_system_alert_delete_children(uintptr_t);
#define OPEN_CFW_SYSTEM_ALERT_DELETE_CHILDREN(o) open_cfw_retained_system_alert_delete_children(o)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_IMAGE_CREATE
uintptr_t open_cfw_retained_system_alert_image_create(uintptr_t);
#define OPEN_CFW_SYSTEM_ALERT_IMAGE_CREATE(o) open_cfw_retained_system_alert_image_create(o)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_IMAGE_SET_SOURCE
void open_cfw_retained_system_alert_image_set_source(uintptr_t, const void *);
#define OPEN_CFW_SYSTEM_ALERT_IMAGE_SET_SOURCE(...) open_cfw_retained_system_alert_image_set_source(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_LABEL_CREATE
uintptr_t open_cfw_retained_system_alert_label_create(uintptr_t);
#define OPEN_CFW_SYSTEM_ALERT_LABEL_CREATE(o) open_cfw_retained_system_alert_label_create(o)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_LABEL_SET_TEXT
void open_cfw_retained_system_alert_label_set_text(uintptr_t, const char *);
#define OPEN_CFW_SYSTEM_ALERT_LABEL_SET_TEXT(...) open_cfw_retained_system_alert_label_set_text(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_TRANSLATION_ID
uint32_t open_cfw_retained_system_alert_translation_id(const char *);
#define OPEN_CFW_SYSTEM_ALERT_TRANSLATION_ID(s) open_cfw_retained_system_alert_translation_id(s)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_TRANSLATION
const char *open_cfw_retained_system_alert_translation(const char *, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_TRANSLATION(s,i) open_cfw_retained_system_alert_translation((s),(i))
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_ROLE
uint32_t open_cfw_retained_system_alert_role(void);
#define OPEN_CFW_SYSTEM_ALERT_ROLE() open_cfw_retained_system_alert_role()
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_DISPLAY_ACTIVE
uint32_t open_cfw_retained_system_alert_display_active(void);
#define OPEN_CFW_SYSTEM_ALERT_DISPLAY_ACTIVE() open_cfw_retained_system_alert_display_active()
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_POST_SELF
uint32_t open_cfw_retained_system_alert_post_self(uint32_t, const void *, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_POST_SELF(...) open_cfw_retained_system_alert_post_self(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_NOTIFY_STATE
uint32_t open_cfw_retained_system_alert_notify_state(uint32_t, const void *, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_NOTIFY_STATE(...) open_cfw_retained_system_alert_notify_state(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_SEND_EVENT
uint32_t open_cfw_retained_system_alert_send_event(uint32_t, const void *, uint32_t, uint32_t);
#define OPEN_CFW_SYSTEM_ALERT_SEND_EVENT(...) open_cfw_retained_system_alert_send_event(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SYSTEM_ALERT_TICK
uint32_t open_cfw_retained_system_alert_tick(void);
#define OPEN_CFW_SYSTEM_ALERT_TICK() open_cfw_retained_system_alert_tick()
#endif

#define OPEN_CFW_SYSTEM_ALERT_DISCONNECT_IMAGE ((const void *)(uintptr_t)0x007747e4u)
#define OPEN_CFW_SYSTEM_ALERT_CONNECT_IMAGE ((const void *)(uintptr_t)0x00772928u)
#define OPEN_CFW_SYSTEM_ALERT_DISCONNECT_ID "ID_GENERAL_RING_DISCONNECT"
#define OPEN_CFW_SYSTEM_ALERT_CONNECT_ID "ID_GENERAL_RING_CONNECT"

void open_cfw_system_alert_set_box_padding(uintptr_t, uint32_t, uint32_t);
uint32_t open_cfw_system_alert_common_data_handler(uint32_t, const uint8_t *, uint32_t);
uint32_t open_cfw_system_alert_page_event_handler(uintptr_t, const void *, uint32_t, const void *);
void open_cfw_system_alert_main_page_init(uintptr_t, const void *, uint32_t);
uint32_t open_cfw_system_alert_send_event_throttled(uint8_t);
void open_cfw_system_alert_reflash_event_handler(const uint8_t *, uint32_t);
uint32_t open_cfw_system_alert_ui_event_handler(uint32_t, const void *, uint32_t, uintptr_t);

#if !defined(OPEN_CFW_SYSTEM_ALERT_PADDING_ONLY) && !defined(OPEN_CFW_SYSTEM_ALERT_COMMON_ONLY) && !defined(OPEN_CFW_SYSTEM_ALERT_PAGE_EVENT_ONLY) && !defined(OPEN_CFW_SYSTEM_ALERT_INIT_ONLY) && !defined(OPEN_CFW_SYSTEM_ALERT_THROTTLED_ONLY) && !defined(OPEN_CFW_SYSTEM_ALERT_REFLASH_ONLY) && !defined(OPEN_CFW_SYSTEM_ALERT_UI_EVENT_ONLY)
#define OPEN_CFW_SYSTEM_ALERT_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_SYSTEM_ALERT_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_ALERT_PAGE_EVENT_ONLY) || defined(OPEN_CFW_SYSTEM_ALERT_REFLASH_ONLY) || defined(OPEN_CFW_SYSTEM_ALERT_UI_EVENT_ONLY)
static __attribute__((always_inline)) inline void open_cfw_system_alert_set_sync_state(uint8_t visible)
{
    OPEN_CFW_SYSTEM_ALERT_VISIBLE = visible;
    OPEN_CFW_SYSTEM_ALERT_ANIMATION_TICKS = OPEN_CFW_SYSTEM_ALERT_DURATION;
}
#endif

#if defined(OPEN_CFW_SYSTEM_ALERT_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_ALERT_PADDING_ONLY)
__attribute__((used, noinline))
void open_cfw_system_alert_set_box_padding(uintptr_t object, uint32_t value, uint32_t selector)
{
    OPEN_CFW_SYSTEM_ALERT_SET_PAD_TOP(object, value, selector);
    OPEN_CFW_SYSTEM_ALERT_SET_PAD_BOTTOM(object, value, selector);
    OPEN_CFW_SYSTEM_ALERT_SET_PAD_LEFT(object, value, selector);
    OPEN_CFW_SYSTEM_ALERT_SET_PAD_RIGHT(object, value, selector);
}
#endif

#if defined(OPEN_CFW_SYSTEM_ALERT_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_ALERT_COMMON_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_system_alert_common_data_handler(uint32_t event, const uint8_t *data, uint32_t length)
{
    (void)event;
    if (data == NULL || length == 0u) return 0u;
    OPEN_CFW_SYSTEM_ALERT_TYPE = data[0];
    if (OPEN_CFW_SYSTEM_ALERT_ROLE() == OPEN_CFW_SYSTEM_ALERT_ROLE_MASTER && OPEN_CFW_SYSTEM_ALERT_DISPLAY_ACTIVE() == 1u) {
        (void)OPEN_CFW_SYSTEM_ALERT_POST_SELF(OPEN_CFW_SYSTEM_ALERT_APP_ID, NULL, 0u, 200u);
    }
    return 0u;
}
#endif

#if defined(OPEN_CFW_SYSTEM_ALERT_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_ALERT_PAGE_EVENT_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_system_alert_page_event_handler(uintptr_t object, const void *event_data, uint32_t event, const void *context)
{
    uint8_t exit_event = OPEN_CFW_SYSTEM_ALERT_EXIT_EVENT;
    (void)object; (void)event_data; (void)context;
    if (event == 0x0au || event == 0x48u || event == 0x44u || event == 0x45u) {
        uint32_t role = OPEN_CFW_SYSTEM_ALERT_ROLE();
        if (role != OPEN_CFW_SYSTEM_ALERT_ROLE_SLAVE && role == OPEN_CFW_SYSTEM_ALERT_ROLE_MASTER) {
            open_cfw_system_alert_set_sync_state(0u);
            (void)OPEN_CFW_SYSTEM_ALERT_NOTIFY_STATE(OPEN_CFW_SYSTEM_ALERT_APP_ID, NULL, 0u, 0u);
        }
    } else if (event == 0x4du) {
        open_cfw_system_alert_set_sync_state(1u);
        if (OPEN_CFW_SYSTEM_ALERT_ROLE() == OPEN_CFW_SYSTEM_ALERT_ROLE_MASTER) {
            (void)OPEN_CFW_SYSTEM_ALERT_POST_SELF(OPEN_CFW_SYSTEM_ALERT_APP_ID, &exit_event, 1u, 3000u);
        }
    }
    return 1u;
}
#endif

#if defined(OPEN_CFW_SYSTEM_ALERT_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_ALERT_INIT_ONLY)
__attribute__((used, noinline))
void open_cfw_system_alert_main_page_init(uintptr_t parent, const void *data, uint32_t length)
{
    uintptr_t root;
    uintptr_t content;
    uint32_t black;
    (void)data; (void)length;
    root = OPEN_CFW_SYSTEM_ALERT_OBJECT_CREATE(parent);
    OPEN_CFW_SYSTEM_ALERT_ROOT = root;
    OPEN_CFW_SYSTEM_ALERT_SET_WIDTH(root, 0x3fffffffu);
    OPEN_CFW_SYSTEM_ALERT_SET_HEIGHT(root, 40u);
    OPEN_CFW_SYSTEM_ALERT_SET_FLEX_FLOW(root, 2u, 0u, 0u);
    OPEN_CFW_SYSTEM_ALERT_CLEAR_FLAGS(root, 0x2004u);
    OPEN_CFW_SYSTEM_ALERT_SET_LAYOUT(root, 0u);
    black = OPEN_CFW_SYSTEM_ALERT_COLOR(0u);
    OPEN_CFW_SYSTEM_ALERT_SET_BG_COLOR(root, black, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_BG_OPACITY(root, 0xffu, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_TEXT_COLOR(root, black, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_TEXT_ALIGN(root, 0u, 0u);
    open_cfw_system_alert_set_box_padding(root, 0u, 0u);

    content = OPEN_CFW_SYSTEM_ALERT_OBJECT_CREATE(root);
    OPEN_CFW_SYSTEM_ALERT_CONTENT = content;
    OPEN_CFW_SYSTEM_ALERT_SET_WIDTH(content, 0x3fffffffu);
    OPEN_CFW_SYSTEM_ALERT_SET_HEIGHT(content, 40u);
    OPEN_CFW_SYSTEM_ALERT_SET_RADIUS(content, OPEN_CFW_SYSTEM_ALERT_ROLE() == OPEN_CFW_SYSTEM_ALERT_ROLE_MASTER ? 0u : 16u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_BORDER_WIDTH(content, 0u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_LAYOUT(content, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_ALIGN(content, 12u);
    OPEN_CFW_SYSTEM_ALERT_SET_BG_OPACITY(content, 0u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_SCROLLBAR_MODE(content, 10u);
    OPEN_CFW_SYSTEM_ALERT_SET_TEXT_COLOR(content, OPEN_CFW_SYSTEM_ALERT_COLOR(0xffffffu), 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_TEXT_ALIGN(content, 1u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_PAD_LEFT(content, 0u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_PAD_RIGHT(content, 0u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_PAD_TOP(content, 12u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_PAD_BOTTOM(content, 12u, 0u);
}
#endif

#if defined(OPEN_CFW_SYSTEM_ALERT_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_ALERT_THROTTLED_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_system_alert_send_event_throttled(uint8_t event)
{
    uint32_t now = OPEN_CFW_SYSTEM_ALERT_TICK();
    if (OPEN_CFW_SYSTEM_ALERT_LAST_TICK == 0u) {
        OPEN_CFW_SYSTEM_ALERT_LAST_TICK = now;
    } else if (OPEN_CFW_SYSTEM_ALERT_LAST_TICK < now) {
        if (now - OPEN_CFW_SYSTEM_ALERT_LAST_TICK < OPEN_CFW_SYSTEM_ALERT_THROTTLE_TICKS) return 0u;
        OPEN_CFW_SYSTEM_ALERT_LAST_TICK = now;
    }
    return OPEN_CFW_SYSTEM_ALERT_SEND_EVENT(OPEN_CFW_SYSTEM_ALERT_APP_ID, &event, 1u, 0u);
}
#endif

#if defined(OPEN_CFW_SYSTEM_ALERT_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_ALERT_REFLASH_ONLY)
static __attribute__((always_inline)) inline void open_cfw_system_alert_render(const void *image_source, const char *translation_id)
{
    uintptr_t image;
    uintptr_t label;
    OPEN_CFW_SYSTEM_ALERT_DELETE_CHILDREN(OPEN_CFW_SYSTEM_ALERT_CONTENT);
    image = OPEN_CFW_SYSTEM_ALERT_IMAGE_CREATE(OPEN_CFW_SYSTEM_ALERT_CONTENT);
    OPEN_CFW_SYSTEM_ALERT_IMAGE_SET_SOURCE(image, image_source);
    OPEN_CFW_SYSTEM_ALERT_SET_WIDTH(image, 24u);
    OPEN_CFW_SYSTEM_ALERT_SET_HEIGHT(image, 24u);
    OPEN_CFW_SYSTEM_ALERT_SET_RADIUS(image, 0u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_BORDER_WIDTH(image, 8u, 0u);
    OPEN_CFW_SYSTEM_ALERT_ADD_FLAGS(image, 0x10000u);
    OPEN_CFW_SYSTEM_ALERT_CLEAR_FLAGS(image, 16u);
    label = OPEN_CFW_SYSTEM_ALERT_LABEL_CREATE(OPEN_CFW_SYSTEM_ALERT_CONTENT);
    OPEN_CFW_SYSTEM_ALERT_LABEL_SET_TEXT(label, OPEN_CFW_SYSTEM_ALERT_TRANSLATION(translation_id, OPEN_CFW_SYSTEM_ALERT_TRANSLATION_ID(translation_id)));
    OPEN_CFW_SYSTEM_ALERT_SET_WIDTH(label, 0x3fffffffu);
    OPEN_CFW_SYSTEM_ALERT_SET_HEIGHT(label, 0x3fffffffu);
    OPEN_CFW_SYSTEM_ALERT_SET_RADIUS(label, 36u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_BORDER_WIDTH(label, 6u, 0u);
    OPEN_CFW_SYSTEM_ALERT_ADD_FLAGS(label, 0x10000u);
    OPEN_CFW_SYSTEM_ALERT_CLEAR_FLAGS(label, 16u);
    OPEN_CFW_SYSTEM_ALERT_SET_FONT(label, OPEN_CFW_SYSTEM_ALERT_FONT, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_LABEL_BG_COLOR(label, OPEN_CFW_SYSTEM_ALERT_COLOR(0xffffffu), 0u);
    if (OPEN_CFW_SYSTEM_ALERT_ROLE() == OPEN_CFW_SYSTEM_ALERT_ROLE_MASTER) OPEN_CFW_SYSTEM_ALERT_SET_FLEX_FLOW(OPEN_CFW_SYSTEM_ALERT_CONTENT, 9u, 0u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_FLEX_FLOW(OPEN_CFW_SYSTEM_ALERT_ROOT, 2u, 0u, 0u);
    OPEN_CFW_SYSTEM_ALERT_SET_SCROLL_DIR(OPEN_CFW_SYSTEM_ALERT_ROOT, 2u);
}
#endif

#if defined(OPEN_CFW_SYSTEM_ALERT_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_ALERT_REFLASH_ONLY)
__attribute__((used, noinline))
void open_cfw_system_alert_reflash_event_handler(const uint8_t *data, uint32_t length)
{
    if (data != NULL && length != 0u) {
        if (data[0] == OPEN_CFW_SYSTEM_ALERT_EXIT_EVENT) {
            open_cfw_system_alert_set_sync_state(0u);
            (void)OPEN_CFW_SYSTEM_ALERT_NOTIFY_STATE(OPEN_CFW_SYSTEM_ALERT_APP_ID, NULL, 0u, 0u);
        }
        return;
    }
    if (OPEN_CFW_SYSTEM_ALERT_TYPE == 1u) {
        open_cfw_system_alert_render(OPEN_CFW_SYSTEM_ALERT_DISCONNECT_IMAGE, OPEN_CFW_SYSTEM_ALERT_DISCONNECT_ID);
    } else if (OPEN_CFW_SYSTEM_ALERT_TYPE == 2u) {
        open_cfw_system_alert_render(OPEN_CFW_SYSTEM_ALERT_CONNECT_IMAGE, OPEN_CFW_SYSTEM_ALERT_CONNECT_ID);
    }
}
#endif

#if defined(OPEN_CFW_SYSTEM_ALERT_BUILD_ALL) || defined(OPEN_CFW_SYSTEM_ALERT_UI_EVENT_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_system_alert_ui_event_handler(uint32_t type, const void *data, uint32_t length, uintptr_t parent)
{
    if (type == 2u) {
        open_cfw_system_alert_main_page_init(parent, data, length);
        OPEN_CFW_SYSTEM_ALERT_PAGE_DESCRIPTOR[1] = OPEN_CFW_SYSTEM_ALERT_ROOT;
        open_cfw_system_alert_set_sync_state(1u);
    } else if (type == 3u) {
        open_cfw_system_alert_reflash_event_handler((const uint8_t *)data, length);
    } else if (type == 5u) {
        open_cfw_system_alert_set_sync_state(0u);
    }
    return 0u;
}
#endif
