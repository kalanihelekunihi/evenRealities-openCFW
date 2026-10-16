/* Native Setting_ui_event_handler 0x467e68..0x467f02. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_uart_hub_calibration_display_update_4a7472(uint32_t);
extern void audio_uart_hub_calibration_success_display_4a76e4(void);
extern uint8_t *audio_settings_get_config_46b44c(void);
extern uint32_t audio_settings_notify_device_status(void);
extern uint32_t audio_settings_notify_recalibration_status_49beac(uint32_t);
extern uint32_t audio_uart_calibration_snapshot_200749a8;
extern uint8_t audio_uart_calibration_status_2007501c;
extern uint8_t audio_uart_registry_context_20003a40[];

static const char module[] = "setting";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[] = "Setting_ui_event_handler";
static const char start_message[] = "setting DISPLAY_STARTUP";
static const char start_short[] = "[setting]setting DISPLAY_STARTUP";

uint64_t audio_uart_registry_callback_467e68(uint32_t event, uint32_t unused,
                                                uint32_t parameter,
                                                uint32_t display) {
    (void)unused;
    if (event == 2u) {
        if ((audio_log_flags() & 2u) != 0u) {
            parameter = 0x305u;
            audio_log_extended(4u, module, path, function, 0x305u, start_message);
        }
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10000000u, start_short, start_short);
        audio_uart_hub_calibration_display_update_4a7472(display);
        *(uint32_t *)(void *)(audio_uart_registry_context_20003a40 + 4u) =
            audio_uart_calibration_snapshot_200749a8;
    } else if (event == 3u) {
        audio_uart_hub_calibration_success_display_4a76e4();
        *(uint32_t *)(void *)(audio_settings_get_config_46b44c() + 0x40u) = 1u;
        (void)audio_settings_notify_device_status();
    } else if (event == 5u) {
        *(uint32_t *)(void *)(audio_settings_get_config_46b44c() + 0x40u) = 0u;
        audio_uart_calibration_status_2007501c = 0u;
        (void)audio_settings_notify_recalibration_status_49beac(1u);
        (void)audio_settings_notify_device_status();
    }
    return (uint64_t)parameter << 32;
}
