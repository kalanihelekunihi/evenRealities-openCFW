/* Apollo page selection traversal 0x44d63a..0x44d779.
 * The active-page lookup at 0x44d77a remains an explicit lower provider. */
#include <stdint.h>

extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *, uint32_t);
extern void *audio_uart_page_overlay_44dca2(const void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_display_size_changed(void *);
extern void *audio_uart_page_context_find_44d77a(void *);

typedef void *(*page_first_fn)(void *);
typedef void *(*page_next_fn)(void *, void *);

static uint32_t word_at(const void *base, uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)base + offset);
}

uint32_t audio_uart_page_update_core_44d63a(void *page, page_first_fn first,
                                              page_next_fn next) {
    uint8_t *const p = (uint8_t *)page;
    if ((p[0x1cu] & 1u) != 0u)
        return 0u;

    uint32_t *node = (uint32_t *)(uintptr_t)word_at(page, 0x0cu);
    uint32_t *start = 0;
    uint32_t first_pass = 1u;
    for (;;) {
        uint32_t from_existing = 1u;
        if (node == 0) {
            if ((p[0x1cu] & 8u) == 0u && start != 0)
                return 0u;
            if (first_pass == 0u)
                return 0u;
            node = (uint32_t *)first(page);
            from_existing = 0u;
            first_pass = 0u;
        }
        if (start == 0) {
            start = node;
            if (node == 0)
                return 0u;
        }
        if (from_existing != 0u) {
            node = (uint32_t *)next(page, node);
            if (node == start)
                return 0u;
        }
        if (node == 0)
            continue;
        uint32_t object = *node;
        /* The native state getter returns the low halfword at object+0x28.
         * Its caller tests the sign of the low byte. */
        if (object == 0 || (int8_t)*(const uint16_t *)(const void *)
                ((const uint8_t *)(uintptr_t)object + 0x28u) < 0)
            continue;
        while (object != 0 &&
               audio_uart_lv_obj_has_flag_43e0e0((void *)(uintptr_t)object, 1u) == 0u)
            object = (uint32_t)(uintptr_t)audio_uart_page_overlay_44dca2(
                (void *)(uintptr_t)object);
        if (object != 0 &&
            audio_uart_lv_obj_has_flag_43e0e0((void *)(uintptr_t)object, 1u) != 0u)
            continue;

        uint32_t *current = (uint32_t *)(uintptr_t)word_at(page, 0x0cu);
        if (node == current)
            return 0u;
        if (current != 0) {
            void *const context = audio_uart_page_context_find_44d77a(page);
            if ((uint8_t)audio_uart_lv_obj_event_451670(
                    (void *)(uintptr_t)*current, 0x14u, context) != 1u)
                return 0u;
            audio_uart_display_size_changed((void *)(uintptr_t)*current);
        }
        *(uint32_t *)(void *)(p + 0x0cu) = (uint32_t)(uintptr_t)node;
        void *const context = audio_uart_page_context_find_44d77a(page);
        if ((uint8_t)audio_uart_lv_obj_event_451670(
                (void *)(uintptr_t)*node, 0x13u, context) != 1u)
            return 0u;
        audio_uart_display_size_changed((void *)(uintptr_t)*node);
        uint32_t const callback = word_at(page, 0x10u);
        if (callback != 0u)
            ((void (*)(void *))(uintptr_t)callback)(page);
        return 1u;
    }
}
