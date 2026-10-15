/* Apollo Main LVGL speed/time packing, native span 0x4505a2..0x450633. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char speed_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_anim.c";
static const char speed_function[] = "lv_anim_speed_clamped";

uint32_t audio_uart_lv_anim_duration_clamp_4505a2(uint32_t speed,
                                                    uint32_t min_time,
                                                    uint32_t max_time) {
    if (speed > 10000u) {
        audio_uart_lvgl_log(2u, speed_source, 0xd8u, speed_function,
                            "speed is truncated to 10000 (was %u)", speed);
        speed = 0x27f6u;
    }
    if (min_time > 10000u) {
        audio_uart_lvgl_log(2u, speed_source, 0xdcu, speed_function,
                            "min_time is truncated to 10000 (was %u)", min_time);
        min_time = 0x27f6u;
    }
    if (max_time > 10000u) {
        audio_uart_lvgl_log(2u, speed_source, 0xe0u, speed_function,
                            "max_time is truncated to 10000 (was %u)", max_time);
        max_time = 0x27f6u;
    }
    return ((speed + 5u) / 10u)
        + (((min_time + 5u) / 10u) << 10)
        + (((max_time + 5u) / 10u) << 20)
        - 0x80000000u;
}
