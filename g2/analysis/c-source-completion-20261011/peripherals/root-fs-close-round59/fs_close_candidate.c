/* Full native4c6ee0..4c6f46, LVGL lv_fs_close. File words:
 * file_d0, driver4, cache8; driver cache_size4, close_cb16;
 * cache buffer12. Native result is truncated to8 bits. */
#include <stdint.h>
extern void audio_uart_lv_heap_free(void *);
uint32_t audio_uart_lv_fs_file_close_4c6ee0(void *file)
{
    volatile uint32_t *f = file;
    if(f[1] == 0u) return 11u;
    if(((volatile uint32_t *)(uintptr_t)f[1])[4] == 0u) return 9u;
    uint32_t file_data = f[0];
    uint32_t driver = f[1];
    uint32_t callback = ((volatile uint32_t *)(uintptr_t)f[1])[4];
    uint32_t result = ((uint32_t (*)(void *,void *))(uintptr_t)callback)
        ((void *)(uintptr_t)driver,(void *)(uintptr_t)file_data);
    if(((volatile uint32_t *)(uintptr_t)f[1])[1] != 0u && f[2] != 0u) {
        if(((volatile uint32_t *)(uintptr_t)f[1])[1] != UINT32_MAX &&
           ((volatile uint32_t *)(uintptr_t)f[2])[3] != 0u) {
            audio_uart_lv_heap_free((void *)(uintptr_t)((volatile uint32_t *)(uintptr_t)f[2])[3]);
        }
        audio_uart_lv_heap_free((void *)(uintptr_t)f[2]);
    }
    f[0] = 0u;
    f[1] = 0u;
    f[2] = 0u;
    return (uint8_t)result;
}
