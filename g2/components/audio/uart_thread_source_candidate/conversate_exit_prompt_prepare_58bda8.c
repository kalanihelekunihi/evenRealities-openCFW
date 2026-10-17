/* Native exit-prompt foreground-app check at 0x58bda8. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_system_close_active_app_get_443504(uint32_t *background,
                                                          uint32_t *foreground);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t level, const char *module,
                               const char *path, const char *function,
                               uint32_t line, const char *format, ...);
extern uint32_t compressed_log_output(uint32_t mask, const char *format,
                                      const char *copy, ...);
extern void audio_system_alert_close_464c36(uint32_t application_id,
                                            uint32_t payload,
                                            uint32_t length,
                                            uint32_t context);

static const char module[] = "exit_prompt";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\exit_prompt.c";
static const char function[] = "common_exit_prompt_check_foreground_app";
static const char message[] = "foreground app exist, stop foreground app(id = %d)";
static const char compact[] =
    "[exit_prompt]foreground app exist, stop foreground app(id = %d)";

void audio_conversate_exit_prompt_prepare_58bda8(void) {
    if (audio_uart_device_role_get() != 1u)
        return;
    uint32_t background = 0u;
    uint32_t foreground = 0u;
    (void)audio_system_close_active_app_get_443504(&background, &foreground);
    if (foreground == 0u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x21u,
                           message, foreground);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c400000u, compact, compact,
                                    foreground);
    audio_system_alert_close_464c36((uint16_t)foreground, 0u, 0u, 0u);
}
