#include <stdint.h>

/* Stock Apollo Main 0x44daca..0x44dbc3: reorder a child in its parent's list. */
extern void *audio_uart_page_overlay_44dca2(const void *object);
extern uint32_t audio_uart_lv_child_count_44ddea(void *object);
extern int32_t audio_uart_lv_child_index_44de92(void *object);
extern uint32_t audio_uart_lv_obj_event_451670(void *object, uint32_t code,
                                               void *param);
extern void audio_uart_display_size_changed(void *object);

void audio_uart_page_44daca(void *child, int32_t target)
{
    if (child == 0) {
        /* The stock null-child path asserts and deliberately faults. */
        __builtin_trap();
    }

    uint8_t *parent = (uint8_t *)audio_uart_page_overlay_44dca2(child);
    if (parent == 0) {
        /* Stock logs an error and returns. */
        return;
    }

    uint32_t count = audio_uart_lv_child_count_44ddea(parent);
    int32_t current = audio_uart_lv_child_index_44de92(child);
    if (current < 0) {
        /* The stock index failure path asserts and deliberately faults. */
        __builtin_trap();
    }

    if (target < 0) target += (int32_t)count;
    if (target < 0 || (uint32_t)target >= count || target == current) return;

    /* The parent's child-array pointer is held through a pointer at offset 8. */
    uintptr_t **children_slot = *(uintptr_t ***)(void *)(parent + 8);
    uintptr_t *children = *children_slot;
    if (target < current) {
        for (int32_t i = current; i > target; --i) children[i] = children[i - 1];
    } else {
        for (int32_t i = current; i < target; ++i) children[i] = children[i + 1];
    }
    children[target] = (uintptr_t)child;
    (void)audio_uart_lv_obj_event_451670(parent, 0x2au, 0);
    audio_uart_display_size_changed(parent);
}
