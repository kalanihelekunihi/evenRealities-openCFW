/* Apollo Main bounce_animation_play, native 0x58a680..0x58a7d1. */
#include <stdint.h>

extern volatile uint8_t audio_conversate_bounce_state_20073e14[16];
extern void audio_conversate_bounce_stop_58a7d2(uint32_t);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_lv_anim_start_450408(void *);
extern void audio_uart_lv_anim_path_450672(void);
extern void audio_conversate_bounce_y_58a3fc(uint32_t, int32_t);
extern void audio_conversate_bounce_phase1_done_58a408(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "bounce.anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\bounce_anim.c";
static const char function[] = "bounce_animation_play";
static const char invalid[] = "obj is NULL";
static const char invalid_compact[] = "[bounce.anim]obj is NULL";
static const char top[] = "TOP_TO_BOTTOM";
static const char bottom[] = "BOTTOM_TO_TOP";
static const char starting[] =
    "Starting bounce animation: direction=%s, distance=%dpx, total_duration=%dms";
static const char starting_compact[] =
    "[bounce.anim]Starting bounce animation: direction=%s, distance=%dpx, total_duration=%dms";
static const char phase1[] = "Phase 1 animation started: duration=%dms";
static const char phase1_compact[] =
    "[bounce.anim]Phase 1 animation started: duration=%dms";

void audio_conversate_main_list_scroll_58a680(uint32_t object, uint32_t y,
                                                uint32_t direction, uint32_t extra,
                                                uint32_t ignored_a, uint32_t ignored_b) {
    (void)ignored_a;
    (void)ignored_b;
    if (object == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x9cu, invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, invalid_compact, invalid_compact);
        return;
    }
    audio_conversate_bounce_stop_58a7d2(object);
    volatile uint32_t *const state =
        (volatile uint32_t *)(void *)audio_conversate_bounce_state_20073e14;
    state[0] = object;
    state[1] = y;
    audio_conversate_bounce_state_20073e14[8] = (uint8_t)direction;
    state[3] = extra;
    const uint32_t target = y + ((uint8_t)direction == 0u ? (uint32_t)-30 : 30u);
    const char *const label = (uint8_t)direction == 0u ? top : bottom;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0xb9u, starting, label, 30u, 400u);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0cc00000u, starting_compact,
                                    starting_compact, label, 30u, 400u);
    uint32_t animation[24];
    audio_uart_lv_anim_init_4503d6(animation);
    animation[0] = object;
    animation[1] = (uint32_t)(uintptr_t)audio_conversate_bounce_y_58a3fc;
    audio_uart_lv_anim_values_4506ce(animation, (int32_t)y, (int32_t)target);
    animation[12] = 200u;
    animation[8] = (uint32_t)(uintptr_t)audio_uart_lv_anim_path_450672;
    animation[4] = (uint32_t)(uintptr_t)audio_conversate_bounce_phase1_done_58a408;
    animation[7] = (uint32_t)(uintptr_t)state;
    (void)audio_uart_lv_anim_start_450408(animation);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0xc7u, phase1, 200u);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c400000u, phase1_compact, phase1_compact, 200u);
}
