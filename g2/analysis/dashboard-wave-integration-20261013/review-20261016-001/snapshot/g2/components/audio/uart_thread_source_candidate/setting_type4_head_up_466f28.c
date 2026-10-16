/* Stock setting_handle_head_up_setting, 0x466f28..0x467134. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint8_t *audio_settings_get_config_46b44c(void);
extern uint32_t audio_uart_service_mode(void);
extern void audio_system_alert_close_464c36(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_uart_master_display_start(uint32_t, const void *, uint16_t, uint32_t);
extern void audio_settings_notify_recalibration_status_49beac(uint32_t);
extern void audio_setting_head_up_configure_46c524(void);
extern uint8_t audio_uart_calibration_status_2007501c;

static const char module[] = "setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[] = "setting_handle_head_up_setting";
static const char null_format[] = "head_up_data is NULL";
static const char null_short[] = "[setting]head_up_data is NULL";
static const char switch_format[] = "Received head up switch: %d";
static const char switch_short[] = "[setting]Received head up switch: %d";
static const char angle_format[] = "Received head up angle: %d";
static const char angle_short[] = "[setting]Received head up angle: %d";
static const char calibration_format[] = "Received head up calibration switch: %d";
static const char calibration_short[] = "[setting]Received head up calibration switch: %d";
static const char showing_format[] = "-----is_calibration_ui_showing:%d";
static const char showing_short[] = "[setting]-----is_calibration_ui_showing:%d";

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

void audio_setting_dispatch_type4_466f28(const uint8_t *data)
{
    if (data == (const uint8_t *)0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x16au, null_format);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u, null_short, null_short);
        return;
    }
    uint32_t type = (uint32_t)data[0] | ((uint32_t)data[1] << 8);
    if (type == 1u || type == 2u || type == 3u) {
        uint32_t value = (uint32_t)data[4] | ((uint32_t)data[5] << 8) |
                         ((uint32_t)data[6] << 16) | ((uint32_t)data[7] << 24);
        if (type == 1u) {
            log_value(0x172u, switch_format, switch_short, value,
                      0x0c400000u, 3u);
            audio_settings_get_config_46b44c()[0xau] = (uint8_t)value;
        } else if (type == 2u) {
            log_value(0x178u, angle_format, angle_short, value,
                      0x0c400000u, 3u);
            uint8_t *config = audio_settings_get_config_46b44c();
            config[0xcu] = (uint8_t)value;
            config[0xdu] = (uint8_t)(value >> 8);
            config[0xeu] = (uint8_t)(value >> 16);
            config[0xfu] = (uint8_t)(value >> 24);
        } else {
            log_value(0x17eu, calibration_format, calibration_short, value,
                      0x0c400000u, 3u);
            log_value(0x17fu, showing_format, showing_short,
                      audio_uart_calibration_status_2007501c,
                      0x10400000u, 4u);
            if (value == 1u) {
                if (audio_uart_calibration_status_2007501c == 1u)
                    return;
                uint32_t role = audio_uart_service_mode();
                uint8_t *config = audio_settings_get_config_46b44c();
                config[0x40u] = 0u; config[0x41u] = 0u;
                config[0x42u] = 0u; config[0x43u] = 0u;
                if ((uint8_t)role == 1u) {
                    audio_system_alert_close_464c36(0u,0u,0u,0u);
                    audio_uart_master_display_start(9u,0,0u,0u);
                }
                audio_uart_calibration_status_2007501c = 1u;
                audio_settings_notify_recalibration_status_49beac(0u);
            } else {
                audio_uart_calibration_status_2007501c = 0u;
                if ((uint8_t)audio_uart_service_mode() == 1u)
                    audio_system_alert_close_464c36(9u,0u,0u,0u);
            }
        }
    }
    if (type != 3u)
        audio_setting_head_up_configure_46c524();
}
