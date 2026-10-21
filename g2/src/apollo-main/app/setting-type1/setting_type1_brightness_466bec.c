/* Stock setting_handle_brightness_setting, 0x466bec..0x466e1c. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_uart_auto_brightness_configure(uint32_t);
extern uint32_t audio_setting_manual_brightness_46c1c8(uint32_t);
extern uint8_t *audio_settings_get_config_46b44c(void);
extern uint32_t audio_setting_brightness_refresh_46c18c(void);

static const char module[] = "setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[] = "setting_handle_brightness_setting";
static const char null_format[] = "bri_data is NULL";
static const char null_short[] = "[setting]bri_data is NULL";
static const char auto_format[] = "Received auto_adjust value: %d";
static const char auto_short[] = "[setting]Received auto_adjust value: %d";
static const char manual_format[] = "[Brightness Level] Received brightness level: %d";
static const char manual_short[] = "[setting][Brightness Level] Received brightness level: %d";
static const char left_format[] = "[Left Calibration] Received level: %d";
static const char left_short[] = "[setting][Left Calibration] Received level: %d";
static const char right_format[] = "[Right Calibration] Received right_calibration: %d";
static const char right_short[] = "[setting][Right Calibration] Received right_calibration: %d";
static const char unknown_format[] = "Unknown brightness type: %d";
static const char unknown_short[] = "[setting]Unknown brightness type: %d";

static void log_value(uint32_t line, const char *long_format,
                      const char *short_format, uint32_t value,
                      uint32_t short_code, uint8_t severity)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line,
                           long_format, value);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(short_code, short_format,
                                    short_format, value);
}

void audio_setting_dispatch_type1_466bec(const uint8_t *data)
{
    if (data == (const uint8_t *)0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0xf1u, null_format);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u, null_short, null_short);
        return;
    }
    uint32_t type = (uint32_t)data[0] | ((uint32_t)data[1] << 8);
    if (type != 1u && type != 2u && type != 3u && type != 4u) {
        log_value(0x11eu, unknown_format, unknown_short, type, 0x08400000u, 2u);
        return;
    }
    uint32_t value = (uint32_t)data[4] | ((uint32_t)data[5] << 8) |
                     ((uint32_t)data[6] << 16) | ((uint32_t)data[7] << 24);
    if (type == 1u) {
        log_value(0xf7u, auto_format, auto_short, value, 0x0c400000u, 3u);
        (void)audio_uart_auto_brightness_configure(value);
    } else if (type == 2u) {
        log_value(0xfcu, manual_format, manual_short, value, 0x0c400000u, 3u);
        (void)audio_setting_manual_brightness_46c1c8(value);
    } else if (type == 3u || type == 4u) {
        if (type == 3u)
            log_value(0x101u, left_format, left_short, value, 0x0c400000u, 3u);
        else
            log_value(0x110u, right_format, right_short, value, 0x0c400000u, 3u);
        uint8_t *config = audio_settings_get_config_46b44c();
        config[type == 3u ? 0x16u : 0x17u] = (uint8_t)(value < 11u ? value : 10u);
        config = audio_settings_get_config_46b44c();
        config[type == 3u ? 0x17u : 0x16u] = 0u;
        (void)audio_setting_brightness_refresh_46c18c();
    }
}
