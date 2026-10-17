/* Apollo Main common_fade_out_animation_with_delay, 0x58c516..0x58c621. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_lv_anim_start_450408(void *);
extern void audio_legal_regulatory_fade_callback_58c12c(void);
extern void audio_uart_lv_anim_path_450672(void);

static const char module[] = "fade.anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\fade_anim.c";
static const char function[] = "common_fade_out_animation_with_delay";
static const char invalid[] =
    "common_fade_out_animation_with_delay: obj is not valid";
static const char invalid_compact[] =
    "[fade.anim]common_fade_out_animation_with_delay: obj is not valid";
static const char started[] =
    "fade out with delay started, delay=%u ms, duration=%u ms";
static const char started_compact[] =
    "[fade.anim]fade out with delay started, delay=%u ms, duration=%u ms";

void audio_conversate_exit_prompt_fade_schedule_58c516(
    uint32_t object, uint32_t duration, uint32_t delay,
    void (*complete)(void)) {
    if (object == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0xd1u, invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, invalid_compact,
                                        invalid_compact);
        return;
    }

    (void)audio_uart_lv_style_unlink_450500((void *)(uintptr_t)object,
                                             (void *)(uintptr_t)audio_legal_regulatory_fade_callback_58c12c);
    uint32_t animation[24];
    audio_uart_lv_anim_init_4503d6(animation);
    animation[0] = object;
    audio_uart_lv_anim_values_4506ce(animation, 255, 0);
    animation[12] = duration != 0u ? duration : 250u;
    animation[13] = 0u - delay;
    animation[1] = (uint32_t)(uintptr_t)audio_legal_regulatory_fade_callback_58c12c;
    animation[8] = (uint32_t)(uintptr_t)audio_uart_lv_anim_path_450672;
    if (complete != 0)
        animation[4] = (uint32_t)(uintptr_t)complete;
    (void)audio_uart_lv_anim_start_450408(animation);

    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0xe2u, started,
                           delay, duration);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10800000u, started_compact,
                                    started_compact, delay, duration);
}
