/* Apollo LV event accessors at 0x4518d8 and 0x4519a0.
 * The first returns an input device; its inherited import name says "reset". */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t level, const char *source,
                               uint32_t line, const char *function,
                               const char *message);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_event.c";
static const char invalid_code[] = "Not interpreted with this event code";
static const char indev_function[] = "lv_event_get_indev";
static const char key_function[] = "lv_event_get_key";

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

void *audio_uart_lv_input_reset_4518d8(void *event) {
    const uint8_t *e = (const uint8_t *)event;
    uint32_t code = word(e + 8u);
    switch (code) {
    case 1u: case 2u: case 3u: case 4u:
    case 8u: case 9u: case 10u: case 11u: case 12u:
    case 14u: case 15u: case 16u: case 17u:
    case 19u: case 20u: case 21u: case 24u: case 25u:
        return (void *)(uintptr_t)word(e + 16u);
    default:
        audio_uart_lvgl_log(2u, source, 0xd0u, indev_function, invalid_code);
        return 0;
    }
}

uint32_t audio_uart_lv_event_param_4519a0(void *event) {
    const uint8_t *e = (const uint8_t *)event;
    if (word(e + 8u) == 17u) {
        uint32_t param = word(e + 16u);
        return param == 0u ? 0u : word((const uint8_t *)(uintptr_t)param);
    }
    audio_uart_lvgl_log(2u, source, 0xf8u, key_function, invalid_code);
    return 0u;
}
