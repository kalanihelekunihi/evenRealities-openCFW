/* LVGL first non-deleting child selector 0x44e164..0x44e1c7. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t, const char *, ...);

void *audio_uart_lv_first_live_child_44e164(void *object) {
    if (object == 0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_tree.c",
            0x2fbu, "lv_obj_get_first_not_deleting_child",
            "Asserted at expression: %s (%s)", "obj != NULL", "NULL pointer");
        for (;;) { }
    }
    const uint8_t *const layer = *(const uint8_t *const *)(const void *)
        ((const uint8_t *)object + 8u);
    if (layer == 0)
        return 0;
    const uint16_t count = *(const uint16_t *)(const void *)(layer + 0x30u);
    const uint32_t *const children = *(const uint32_t *const *)(const void *)layer;
    for (uint32_t i = 0; i < count; ++i) {
        const uint32_t child = children[i];
        const uint16_t flags = *(const uint16_t *)(const void *)
            ((const uint8_t *)(uintptr_t)child + 0x2au);
        if (((flags & 0x1fffu) >> 12u) == 0u)
            return (void *)(uintptr_t)child;
    }
    return 0;
}
