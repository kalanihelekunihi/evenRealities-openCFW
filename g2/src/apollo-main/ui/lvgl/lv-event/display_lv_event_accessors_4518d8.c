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



