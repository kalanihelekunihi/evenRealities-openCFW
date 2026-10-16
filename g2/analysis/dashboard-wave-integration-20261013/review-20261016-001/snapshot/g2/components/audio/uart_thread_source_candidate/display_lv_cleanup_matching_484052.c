/* Apollo Main deferred-callback cleanup 0x484052..0x4840a9 and callback
 * dispatch 0x4840ac..0x4840c5. */
#include <stdint.h>

extern void *audio_uart_lv_timer_iter_4645ec(void *);
extern void audio_uart_lv_timer_remove_4644ee(void *);
extern void audio_uart_lv_heap_free(void *);

void audio_uart_lv_async_dispatch_4840ac(void *timer) {
    uint8_t *node = (uint8_t *)timer;
    uint8_t *arg = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)(node + 0x0cu);
    uint32_t callback = *(uint32_t *)(void *)arg;
    uint32_t user = *(uint32_t *)(void *)(arg + 4u);
    audio_uart_lv_timer_remove_4644ee(timer);
    audio_uart_lv_heap_free(arg);
    ((void (*)(void *))(uintptr_t)callback)((void *)(uintptr_t)user);
}

uint32_t audio_uart_lv_cleanup_matching_484052(void *callback, void *user) {
    uint32_t removed = 0u;
    for (uint8_t *node = (uint8_t *)audio_uart_lv_timer_iter_4645ec(0);
         node != 0;) {
        uint8_t *next = (uint8_t *)audio_uart_lv_timer_iter_4645ec(node);
        if (*(uint32_t *)(void *)(node + 8u) ==
            (uint32_t)(uintptr_t)audio_uart_lv_async_dispatch_4840ac) {
            uint8_t *arg = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)(node + 0x0cu);
            if (*(uint32_t *)(void *)arg == (uint32_t)(uintptr_t)callback &&
                *(uint32_t *)(void *)(arg + 4u) == (uint32_t)(uintptr_t)user) {
                audio_uart_lv_timer_remove_4644ee(node);
                audio_uart_lv_heap_free(arg);
                removed = 1u;
            }
        }
        node = next;
    }
    return removed;
}
