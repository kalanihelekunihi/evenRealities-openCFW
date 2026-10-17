/* Native exit-prompt step-two callback at 0x58bebc. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t level, const char *module,
                               const char *path, const char *function,
                               uint32_t line, const char *format, ...);
extern uint32_t compressed_log_output(uint32_t mask, const char *format,
                                      const char *copy, ...);
extern uint32_t audio_conversate_exit_prompt_state_200745d0[3];
extern uint32_t audio_conversate_exit_prompt_hold_20000be4;
extern void audio_conversate_exit_prompt_fade_step3_58be1a(void);
extern void audio_conversate_exit_prompt_fade_schedule_58c516(
    uint32_t app_id, uint32_t duration, uint32_t hold_ms,
    void (*complete)(void));

static const char module[] = "exit_prompt";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\exit_prompt.c";
static const char function[] = "common_exit_prompt_fade_cb_step2";
static const char message[] = "step 2: hold %u ms then fade out";
static const char compact[] =
    "[exit_prompt]step 2: hold %u ms then fade out";

void audio_conversate_exit_prompt_fade_step_58bebc(void) {
    const uint32_t hold_ms = audio_conversate_exit_prompt_hold_20000be4;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x36u,
                           message, hold_ms);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c400000u, compact, compact,
                                    audio_conversate_exit_prompt_hold_20000be4);
    audio_conversate_exit_prompt_fade_schedule_58c516(
        audio_conversate_exit_prompt_state_200745d0[0], 250u,
        audio_conversate_exit_prompt_hold_20000be4,
        audio_conversate_exit_prompt_fade_step3_58be1a);
}
