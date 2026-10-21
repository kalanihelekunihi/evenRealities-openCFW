/* Native exit-prompt completion callback (logged as step 4) at 0x58be1a. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t level, const char *module,
                               const char *path, const char *function,
                               uint32_t line, const char *format, ...);
extern uint32_t compressed_log_output(uint32_t mask, const char *format,
                                      const char *copy, ...);
extern uint8_t audio_uart_device_role_get(void);
extern void audio_conversate_exit_prompt_prepare_58bda8(void);
extern void audio_system_alert_close_464c36(uint32_t application_id,
                                            uint32_t payload,
                                            uint32_t length,
                                            uint32_t context);
extern uint32_t audio_conversate_exit_prompt_state_200745d0[3];

static const char module[] = "exit_prompt";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\exit_prompt.c";
static const char function[] = "common_exit_prompt_fade_cb_step4";
static const char step[] = "step 4";
static const char step_short[] = "[exit_prompt]step 4";
static const char completed[] = "exit prompt show completed";
static const char completed_short[] = "[exit_prompt]exit prompt show completed";

void audio_conversate_exit_prompt_fade_step3_58be1a(void) {
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x28u, step);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c000000u, step_short, step_short);
    if (audio_uart_device_role_get() == 1u) {
        audio_conversate_exit_prompt_prepare_58bda8();
        audio_system_alert_close_464c36(
            (uint16_t)audio_conversate_exit_prompt_state_200745d0[2],
            0u, 0u, 0u);
    }
    audio_conversate_exit_prompt_state_200745d0[0] = 0u;
    audio_conversate_exit_prompt_state_200745d0[1] = 0u;
    audio_conversate_exit_prompt_state_200745d0[2] = 0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x31u, completed);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c000000u, completed_short,
                                    completed_short);
}
