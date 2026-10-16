/* Stock system_close_common_data_handler, 0x469d48..0x469e66. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_log_wake_allowed(void);
extern uint32_t audio_system_close_active_app_get_443504(uint32_t *, uint32_t *);
extern uint32_t audio_system_alert_command_45a8ee(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

volatile uint8_t audio_system_close_selected_20075026;
volatile uint32_t audio_system_close_payload_20074a04;

static const char module[] = "system_close";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\SystemClose\\systemClose.c";
static const char function[] = "system_close_common_data_handler";
static const char length_message[] = "system_close_common_data_handler: len = %d";
static const char length_short[] = "[system_close]system_close_common_data_handler: len = %d";
static const char app_message[] = "unauthorized app id = %d";
static const char app_short[] = "[system_close]unauthorized app id = %d";

static void log_bad(uint32_t line, const char *message, const char *compact,
                    uint32_t value)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, function, line, message, value);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x08400000u, compact, compact, value);
}

uint32_t audio_uart_registry_callback_469d48(uint32_t ignored,
                                               const uint8_t *payload,
                                               uint32_t length,
                                               uint32_t detail)
{
    (void)ignored; (void)detail;
    if (length != 5u) {
        log_bad(0x93u, length_message, length_short, length);
        return UINT32_MAX;
    }
    audio_system_close_selected_20075026 = payload[0];
    audio_system_close_payload_20074a04 =
        (uint32_t)payload[1] | ((uint32_t)payload[2] << 8u) |
        ((uint32_t)payload[3] << 16u) | ((uint32_t)payload[4] << 24u);
    if (audio_uart_device_role_get() == 1u && audio_log_wake_allowed() == 1u) {
        uint32_t app = 0u, status = 0u;
        (void)audio_system_close_active_app_get_443504(&app, &status);
        if (status != 0u || (app != 8u && app != 11u && app != 5u &&
            app != 6u && app != 0xe0u && app != 0xffeu)) {
            log_bad(0xa3u, app_message, app_short, app);
            return UINT32_MAX;
        }
        (void)audio_system_alert_command_45a8ee(0x22u, 0u, 0u, 100u);
    }
    return 0u;
}
