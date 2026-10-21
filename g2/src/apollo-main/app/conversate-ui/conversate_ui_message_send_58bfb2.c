/* Native common exit-prompt sender at 0x58bfb2. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t level, const char *module,
                               const char *path, const char *function,
                               uint32_t line, const char *format, ...);
extern uint32_t compressed_log_output(uint32_t mask, const char *format,
                                      const char *copy, ...);
extern uint32_t audio_uart_lv_style_unlink_450500(void *object, void *style);
extern void audio_conversate_exit_prompt_prepare_58bda8(void);
extern void audio_conversate_exit_prompt_show_58bf12(void);
extern void audio_terminal_fade_out_58c426(uint32_t object, uint32_t duration,
                                            void (*complete)(void));

__attribute__((used, section(".g2_conversate_exit_prompt_state_200745d0")))
uint32_t audio_conversate_exit_prompt_state_200745d0[3];
__attribute__((used, section(".g2_conversate_exit_prompt_hold_20000be4")))
uint32_t audio_conversate_exit_prompt_hold_20000be4;

static const char module[] = "exit_prompt";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\exit_prompt.c";
static const char function[] = "common_exit_prompt_show";
static const char invalid[] = "obj is not valid";
static const char invalid_short[] = "[exit_prompt]obj is not valid";
static const char prompt[] = "exit prompt: text=%s, app_id=%u, text_hold_ms=%u";
static const char prompt_short[] =
    "[exit_prompt]exit prompt: text=%s, app_id=%u, text_hold_ms=%u";

uint32_t audio_conversate_ui_message_send_58bfb2(uint32_t app_id,
                                                   uint32_t text,
                                                   uint32_t event,
                                                   uint32_t animated,
                                                   uint32_t hold_ms) {
    if (app_id == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x50u, invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, invalid_short,
                                        invalid_short);
        return UINT32_MAX;
    }
    const uint32_t effective_hold = hold_ms != 0u ? hold_ms : 750u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x54u, prompt,
                           text, event, effective_hold);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0cc00000u, prompt_short,
                                    prompt_short, text, event, effective_hold);
    (void)audio_uart_lv_style_unlink_450500((void *)(uintptr_t)app_id, 0);
    audio_conversate_exit_prompt_state_200745d0[0] = app_id;
    audio_conversate_exit_prompt_state_200745d0[1] = text;
    audio_conversate_exit_prompt_state_200745d0[2] = event;
    audio_conversate_exit_prompt_hold_20000be4 = effective_hold;
    audio_conversate_exit_prompt_prepare_58bda8();
    if ((uint8_t)animated != 0u)
        audio_terminal_fade_out_58c426(
            audio_conversate_exit_prompt_state_200745d0[0], 250u,
            audio_conversate_exit_prompt_show_58bf12);
    else
        audio_conversate_exit_prompt_show_58bf12();
    return 0u;
}
