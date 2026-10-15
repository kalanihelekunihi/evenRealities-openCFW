/* Native 0x443504: running foreground/background app IDs. */
#include <stdint.h>

extern uint8_t audio_uart_display_state[2]; /* RAM 0x20074f2c */
extern uint32_t audio_uart_display_mode; /* RAM 0x200744dc */
extern uint32_t audio_uart_display_active; /* RAM 0x200744d8 */
extern uint32_t audio_uart_display_background; /* RAM 0x200744e0 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "display_thread";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\display_thread.c";
static const char function[] = "getRunningAppID";
static const char message[] = "startupAppType = 1, background_app_id = %d, foreground_app_id = %d";
static const char compact[] = "[display_thread]startupAppType = 1, background_app_id = %d, foreground_app_id = %d";

static void log_ids(uint32_t line, uint32_t background, uint32_t foreground,
                    uint32_t extra, uint8_t with_extra) {
    if (audio_log_flags() & 2u) {
        if (with_extra)
            audio_log_extended(4u, module, path, function, line, message,
                               background, foreground, extra);
        else
            audio_log_extended(4u, module, path, function, line, message,
                               background, foreground);
    }
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10800000u, compact, compact,
                                    background, foreground);
}

uint32_t audio_get_running_app_ids(uint32_t *background, uint32_t *foreground) {
    if (background == 0 || foreground == 0) return UINT32_MAX;
    if (audio_uart_display_state[0] == 1u) {
        if (audio_uart_display_mode == 1u) {
            *background = audio_uart_display_active;
            *foreground = audio_uart_display_background;
            log_ids(0x244u, *background, *foreground, 0u, 1u);
        } else if (audio_uart_display_mode == 2u) {
            *background = 0u;
            *foreground = audio_uart_display_active;
            log_ids(0x249u, *background, *foreground, 0u, 0u);
        } else {
            *background = 0u;
            *foreground = 0u;
            log_ids(0x24du, *background, *foreground, 0u, 0u);
        }
    } else {
        *background = 0u;
        *foreground = 0u;
        log_ids(0x253u, *background, *foreground, 0u, 0u);
    }
    return 0u;
}
