/* Apollo Main LVGL child deletion, native span 0x44df80..0x44e139.
 * The stock recursive BL at 0x44dfce receives the child in R0 from
 * 0x44dce2; Ghidra omitted this live argument. */
#include <stdint.h>

extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_lv_style_destroy_450228(void *);
extern void *audio_uart_lv_child_get_44dce2(void *, uint32_t);
extern void *audio_uart_lv_obj_group_43e1be(void *);
extern void *audio_uart_lv_input_next_452edc(void *);
extern void audio_uart_lv_input_unlink_44df60(void *, void *);
extern void *audio_uart_lv_input_active_452ffa(void);
extern uint32_t audio_uart_lv_cleanup_matching_484052(void *, void *);
extern void audio_uart_lv_obj_delete_cleanup_44d16e(void *);
extern void *audio_uart_lv_display_for_object(void *);
extern uint32_t audio_uart_lv_child_index_44de92(void *);
extern void *audio_uart_lv_realloc_44f76a(void *, uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern void audio_uart_page_delete_event_filter_44d7b8(void *);

static uint32_t get32(const uint8_t *bytes, uint32_t offset) {
    return *(const uint32_t *)(const void *)(bytes + offset);
}
static void put32(uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(bytes + offset) = value;
}
static uint16_t get16(const uint8_t *bytes, uint32_t offset) {
    return *(const uint16_t *)(const void *)(bytes + offset);
}
static void put16(uint8_t *bytes, uint32_t offset, uint16_t value) {
    *(uint16_t *)(void *)(bytes + offset) = value;
}

void audio_uart_lv_delete_event_callback_44df20(void *object) {
    if (object == 0) {
        audio_uart_lvgl_log(3u, "lv_obj_delete", 0x257u,
                            "lv_obj_delete_async_cb", "object is null");
        __builtin_trap();
    }
    audio_uart_page_delete_event_filter_44d7b8(object);
}

uint32_t audio_uart_lv_input_type_452f00(const void *input) {
    return input == 0 ? 0u : *(const uint8_t *)input;
}

void audio_uart_lv_child_delete_44df80(void *object) {
    uint8_t *const item = (uint8_t *)object;
    if ((get16(item, 0x2au) & 0x1000u) != 0u) return;
    put16(item, 0x2au, (uint16_t)(get16(item, 0x2au) | 0x1000u));
    if ((uint8_t)audio_uart_lv_obj_event_451670(object, 0x29u, 0) == 0u) {
        put16(item, 0x2au, (uint16_t)(get16(item, 0x2au) & 0xefffu));
        return;
    }
    uint8_t *const spec = (uint8_t *)(uintptr_t)get32(item, 8u);
    if (spec != 0) audio_uart_lv_style_destroy_450228(spec + 8u);
    for (void *child = audio_uart_lv_child_get_44dce2(object, 0u);
         child != 0;
         child = audio_uart_lv_child_get_44dce2(object, 0u))
        audio_uart_lv_child_delete_44df80(child);
    void *const group = audio_uart_lv_obj_group_43e1be(object);
    for (uint8_t *input = (uint8_t *)audio_uart_lv_input_next_452edc(0);
         input != 0;
         input = (uint8_t *)audio_uart_lv_input_next_452edc(input)) {
        const uint8_t kind = (uint8_t)audio_uart_lv_input_type_452f00(input);
        if (kind == 1u || kind == 3u) {
            if (get32(input, 0x68u) == (uint32_t)(uintptr_t)object ||
                get32(input, 0x6cu) == (uint32_t)(uintptr_t)object ||
                get32(input, 0x70u) == (uint32_t)(uintptr_t)object)
                audio_uart_lv_input_unlink_44df60(input, object);
            if (get32(input, 0x74u) == (uint32_t)(uintptr_t)object)
                put32(input, 0x74u, 0u);
            if (get32(input, 0x78u) == (uint32_t)(uintptr_t)object)
                put32(input, 0x78u, 0u);
        }
        if (get32(input, 0xb8u) == (uint32_t)(uintptr_t)group &&
            object == audio_uart_lv_input_active_452ffa())
            audio_uart_lv_input_unlink_44df60(input, object);
    }
    while ((uint8_t)audio_uart_lv_cleanup_matching_484052(
        (void *)audio_uart_lv_delete_event_callback_44df20, object) == 1u) {}
    audio_uart_lv_obj_delete_cleanup_44d16e(object);
    uint8_t *const parent = (uint8_t *)(uintptr_t)get32(item, 4u);
    if (parent == 0) {
        uint8_t *const display = (uint8_t *)audio_uart_lv_display_for_object(object);
        uint32_t index = 0u;
        uint32_t count = get32(display, 0x2d4u);
        uint32_t *screens = (uint32_t *)(uintptr_t)get32(display, 0x2b8u);
        while (index < count && screens[index] != (uint32_t)(uintptr_t)object)
            ++index;
        while (index < count - 1u) {
            screens[index] = screens[index + 1u];
            ++index;
        }
        count -= 1u;
        put32(display, 0x2d4u, count);
        screens = (uint32_t *)audio_uart_lv_realloc_44f76a(screens, count << 2);
        put32(display, 0x2b8u, (uint32_t)(uintptr_t)screens);
    } else {
        uint8_t *const parent_spec = (uint8_t *)(uintptr_t)get32(parent, 8u);
        uint32_t *children = (uint32_t *)(uintptr_t)get32(parent_spec, 0u);
        uint32_t index = audio_uart_lv_child_index_44de92(object);
        const uint32_t count = get16(parent_spec, 0x30u);
        while ((uint16_t)index < (int32_t)count - 1) {
            children[(uint16_t)index] = children[(uint16_t)index + 1u];
            ++index;
        }
        const uint16_t next_count = (uint16_t)(count - 1u);
        put16(parent_spec, 0x30u, next_count);
        children = (uint32_t *)audio_uart_lv_realloc_44f76a(children,
                                                               (uint32_t)next_count << 2);
        put32(parent_spec, 0u, (uint32_t)(uintptr_t)children);
    }
    audio_uart_lv_heap_free(object);
}
