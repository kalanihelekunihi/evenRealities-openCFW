/* Apollo LV event layer accessor, native 0x451960..0x45199f. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                               const char *, const char *);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_event.c";
static const char function[] = "lv_event_get_layer";
static const char invalid_code[] = "Not interpreted with this event code";

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

void *audio_uart_lv_event_layer_451960(void *event) {
    const uint8_t *e = (const uint8_t *)event;
    switch (word(e + 8u)) {
    case 0x1cu: case 0x1du: case 0x1eu:
    case 0x1fu: case 0x20u: case 0x21u:
        return (void *)(uintptr_t)word(e + 16u);
    default:
        audio_uart_lvgl_log(2u, source, 0xe0u, function, invalid_code);
        return 0;
    }
}
