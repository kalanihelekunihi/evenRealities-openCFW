/* Apollo Main object group accessor, native span 0x43e1be..0x43e1f9. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

void *audio_uart_lv_obj_group_43e1be(void *object) {
    if (object == 0) {
        audio_uart_lvgl_log(3u, "lv_obj", 0x16cu, "lv_obj_get_group",
                            "object is null");
        __builtin_trap();
    }
    uint8_t *spec = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)((uint8_t *)object + 8u);
    if (spec == 0) return 0;
    return (void *)(uintptr_t)*(uint32_t *)(void *)(spec + 4u);
}
