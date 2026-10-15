/* LVGL allocator names used by the pinned label provider translation units. */
#include <stdint.h>

extern void *audio_uart_lv_heap_alloc(uint32_t);
extern void audio_uart_lv_free(void *);

void *lv_malloc_zeroed(uint32_t bytes) {
    return audio_uart_lv_heap_alloc(bytes);
}
void lv_free(void *pointer) {
    audio_uart_lv_free(pointer);
}
