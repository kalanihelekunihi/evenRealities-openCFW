/* Apollo page unlink 0x44d3b2..0x44d45b; non-null page path. */
#include <stdint.h>

extern void *audio_uart_lv_list_first(void *);
extern void *audio_uart_lv_list_next(void *, void *);
extern void *audio_uart_lv_list_first_482ce4(void *);
extern void audio_uart_lv_list_remove_482c0e(void *, void *);
extern void audio_uart_lv_heap_free(void *);
extern void *audio_uart_page_context_find_44d77a(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_page_notify_44d5f8(void *);

void audio_uart_page_unlink_44d3b2(void *page) {
    uint8_t *const p = (uint8_t *)page;
    uint32_t const layer = *(uint32_t *)(void *)(p + 8u);
    if (layer == 0u)
        return;
    uint8_t *const context = *(uint8_t **)(void *)(uintptr_t)(layer + 4u);
    if (context == 0)
        return;

    uint32_t *current = *(uint32_t **)(void *)(context + 0x0cu);
    if (current != 0 && *current == (uint32_t)(uintptr_t)page) {
        if ((context[0x1cu] & 1u) != 0u)
            context[0x1cu] &= (uint8_t)~1u;
        void *const head = audio_uart_lv_list_first(context);
        if (head == current && audio_uart_lv_list_first_482ce4(context) == current) {
            void *const active = audio_uart_page_context_find_44d77a(context);
            (void)audio_uart_lv_obj_event_451670(page, 0x14u, active);
        }
        else
            audio_uart_page_notify_44d5f8(context);
    }
    current = *(uint32_t **)(void *)(context + 0x0cu);
    if (current != 0 && *current == (uint32_t)(uintptr_t)page)
        *(uint32_t *)(void *)(context + 0x0cu) = 0u;

    uint32_t *node = (uint32_t *)audio_uart_lv_list_first(context);
    while (node != 0 && *node != (uint32_t)(uintptr_t)page)
        node = (uint32_t *)audio_uart_lv_list_next(context, node);
    if (node == 0)
        return;
    audio_uart_lv_list_remove_482c0e(context, node);
    audio_uart_lv_heap_free(node);
    if (*(uint32_t *)(void *)(p + 8u) != 0u)
        *(uint32_t *)(void *)(uintptr_t)(layer + 4u) = 0u;
}
