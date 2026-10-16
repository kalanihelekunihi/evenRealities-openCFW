/* Apollo Main LVGL child index, native span 0x44de92..0x44df1f. */
#include <stdint.h>

extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

int32_t audio_uart_lv_child_index_44de92(void *object) {
    if (object == 0) {
        audio_uart_lvgl_log(3u, "lv_obj", 0x217u, "lv_obj_get_index",
                            "object is null");
        __builtin_trap();
    }
    uint8_t *parent = (uint8_t *)audio_uart_lv_obj_parent_44dca2(object);
    if (parent == 0) return -1;
    uint8_t *spec = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)(parent + 8u);
    uint32_t *children = (uint32_t *)(uintptr_t)*(uint32_t *)(void *)spec;
    uint32_t count = *(uint16_t *)(void *)(spec + 0x30u);
    for (uint32_t index = 0; index < count; ++index) {
        if (children[index] == (uint32_t)(uintptr_t)object)
            return (int32_t)index;
    }
    audio_uart_lvgl_log(3u, "lv_obj", 0x222u, "lv_obj_get_index",
                        "object absent from parent");
    __builtin_trap();
}
