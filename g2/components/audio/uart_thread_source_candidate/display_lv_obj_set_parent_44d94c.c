/* LVGL object reparenting, stock Apollo Main 0x44d94c..0x44dac8.
 * Sequence cross-checked with bundled upstream lv_obj_tree.c. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                               const char *, const char *, ...);
extern void audio_uart_page_invalidate_440656(void *);
extern void audio_uart_lv_obj_setup_layer_43e1fa(void *);
extern int32_t audio_uart_lv_child_index_44de92(void *);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern void *audio_uart_lv_realloc_44f76a(void *, uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lv_scrollbar_invalidate_44f2ca(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_lv_mark_layout_43f648(void *);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}
static uint16_t get16(const uint8_t *p) {
    return (uint16_t)(p[0] | ((uint16_t)p[1] << 8u));
}
static void put16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
}

static void invalid_parent(uint32_t reason) {
    static const char file[] =
        "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_tree.c";
    static const char function[] = "lv_obj_set_parent";
    static const char assertion[] = "Asserted at expression: %s (%s)";
    static const char null_text[] = "NULL pointer";
    if (reason == 0x99u) {
        audio_uart_lvgl_log(2u, file, reason, function,
                            "Can't set the parent of a screen");
        return;
    }
    audio_uart_lvgl_log(3u, file, reason, function, assertion,
                        reason == 0x95u ? "obj != NULL" : "parent != NULL",
                        null_text);
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
}

void audio_uart_lv_obj_set_parent_44d94c(void *object, void *new_parent) {
    if (object == 0) {
        invalid_parent(0x95u);
        return;
    }
    if (new_parent == 0) {
        invalid_parent(0x96u);
        return;
    }
    uint8_t *obj = (uint8_t *)object;
    uint8_t *old_parent = (uint8_t *)(uintptr_t)get32(obj + 4u);
    if (old_parent == 0) {
        invalid_parent(0x99u);
        return;
    }
    if (old_parent == new_parent) return;

    audio_uart_page_invalidate_440656(object);
    audio_uart_lv_obj_setup_layer_43e1fa(new_parent);
    uint8_t *old_spec = (uint8_t *)(uintptr_t)get32(old_parent + 8u);
    int32_t index = audio_uart_lv_child_index_44de92(object);
    uint8_t *old_children = (uint8_t *)(uintptr_t)get32(old_spec);
    for (int32_t i = index;
         i <= (int32_t)audio_uart_lv_child_count_44ddea(old_parent) - 2;
         ++i)
        put32(old_children + (uint32_t)i * 4u,
              get32(old_children + (uint32_t)(i + 1) * 4u));
    uint16_t remaining = (uint16_t)(get16(old_spec + 48u) - 1u);
    put16(old_spec + 48u, remaining);
    if (remaining != 0u)
        put32(old_spec, (uint32_t)(uintptr_t)audio_uart_lv_realloc_44f76a(
            old_children, (uint32_t)remaining * 4u));
    else {
        audio_uart_lv_heap_free(old_children);
        put32(old_spec, 0u);
    }

    uint8_t *parent = (uint8_t *)new_parent;
    uint8_t *new_spec = (uint8_t *)(uintptr_t)get32(parent + 8u);
    uint16_t added = (uint16_t)(get16(new_spec + 48u) + 1u);
    put16(new_spec + 48u, added);
    uint8_t *new_children = (uint8_t *)audio_uart_lv_realloc_44f76a(
        (void *)(uintptr_t)get32(new_spec), (uint32_t)added * 4u);
    put32(new_spec, (uint32_t)(uintptr_t)new_children);
    uint32_t child_count = audio_uart_lv_child_count_44ddea(new_parent);
    put32(new_children + (child_count - 1u) * 4u, (uint32_t)(uintptr_t)obj);
    put32(obj + 4u, (uint32_t)(uintptr_t)parent);

    audio_uart_lv_scrollbar_invalidate_44f2ca(old_parent);
    (void)audio_uart_lv_obj_event_451670(old_parent, 0x2au, object);
    (void)audio_uart_lv_obj_event_451670(old_parent, 0x2cu, 0);
    (void)audio_uart_lv_obj_event_451670(new_parent, 0x2au, object);
    (void)audio_uart_lv_obj_event_451670(new_parent, 0x2bu, 0);
    audio_uart_lv_mark_layout_43f648(object);
    audio_uart_page_invalidate_440656(object);
}
