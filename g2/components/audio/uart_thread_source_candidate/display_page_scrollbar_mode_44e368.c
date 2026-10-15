/* Apollo LVGL scrollbar mode setter 0x44e368..0x44e3c9. */
#include <stdint.h>

extern void audio_uart_lv_obj_setup_layer_43e1fa(void *);
extern void audio_uart_display_size_changed(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t, const char *, ...);

uint32_t audio_uart_page_44e368(void *object, uint32_t mode) {
    if (object == 0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_scroll.c",
            0x3cu, "lv_obj_set_scrollbar_mode", "Asserted at expression: %s (%s)",
            "obj != NULL", "NULL pointer");
        for (;;) { }
    }
    audio_uart_lv_obj_setup_layer_43e1fa(object);
    uint8_t *const layer = *(uint8_t **)(void *)((uint8_t *)object + 8u);
    uint16_t *const flags = (uint16_t *)(void *)(layer + 0x32u);
    if ((*flags & 3u) != (uint8_t)mode) {
        *flags = (uint16_t)((*flags & 0xfffcu) | (mode & 3u));
        audio_uart_display_size_changed(object);
    }
    return mode;
}
