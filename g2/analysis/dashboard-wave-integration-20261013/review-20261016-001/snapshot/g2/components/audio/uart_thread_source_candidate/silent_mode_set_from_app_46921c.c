/* Stock SilentMode_SetStatusFromApp, 0x46921c..0x469388. */
#include <stdint.h>

uint8_t audio_silent_mode_showing_ui_2007501f; /* stock RAM 0x2007501f */
extern uint8_t audio_silent_mode_change_from_app; /* stock RAM 0x2007501e */
extern uint32_t audio_uart_display_active; /* 0x200744d8 */
extern uint32_t audio_uart_display_mode; /* 0x200744dc */
extern uint32_t audio_uart_display_background; /* 0x200744e0 */
extern uint8_t audio_silent_mode_status_get(void); /* 0x46919e */
extern uint32_t audio_log_wake_allowed(void); /* 0x443484 */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern void audio_uart_master_display_stop(uint32_t, const void *, uint16_t, uint32_t); /* 0x464c36 */
extern void audio_uart_task_delay(uint32_t); /* 0x454b4c */
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t, const void *, uint32_t,
                                                    uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "silent_mode";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\Silent_Mode\\silent_mode.c";
static const char function[] = "SilentMode_SetStatusFromApp";
static const char showing[] = "silent mode is showing_ui, not set status from app";
static const char on[] = "Silent mode ON from APP, screen is on, requesting screen off";
static const char send_failure[] = "Failed to send data to both,ret=%d";
static const char showing_short[] = "[silent_mode]silent mode is showing_ui, not set status from app";
static const char on_short[] = "[silent_mode]Silent mode ON from APP, screen is on, requesting screen off";
static const char send_failure_short[] = "[silent_mode]Failed to send data to both,ret=%d";

void audio_silent_mode_set_from_app_46921c(uint32_t value)
{
    if (audio_silent_mode_showing_ui_2007501f != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 0x58u, showing);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10000000u, showing_short, showing_short);
        return;
    }
    audio_silent_mode_change_from_app = 1u;
    const uint8_t current = audio_silent_mode_status_get();
    if ((uint8_t)value != 0u && audio_log_wake_allowed() != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, function, 0x63u, on);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c000000u, on_short, on_short);
        if (audio_uart_device_role_get() == 1u) {
            const uint32_t background = audio_uart_display_background != 0u;
            if (background != 0u)
                audio_uart_master_display_stop(0u, 0, 0u, 0u);
            if (audio_uart_display_active != 0u && audio_uart_display_mode == 1u) {
                if (background != 0u) audio_uart_task_delay(500u);
                audio_uart_master_display_stop(0u, 0, 0u, 0u);
            }
        }
    }
    if (current != (uint8_t)value) {
        uint32_t request = value;
        uint32_t result = audio_sync_send_to_both_ext_464f76(0x10au, &request,
                                                               1u, 0u, 4u);
        if (result != 0u) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(1u, module, path, function, 0x7eu,
                                   send_failure, result);
            if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x04400000u, send_failure_short,
                                            send_failure_short, result);
        }
    }
}
