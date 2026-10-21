/* Apollo Main bounce Y and phase-1 ready callbacks, 0x58a3fc..0x58a597. */
#include <stdint.h>

extern volatile uint8_t audio_conversate_bounce_state_20073e14[16];
extern void audio_uart_page_43f142(uint32_t, int32_t);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_lv_anim_start_450408(void *);
extern void audio_uart_lv_anim_path_450672(void);
extern void audio_conversate_bounce_phase2_y_58a598(uint32_t, int32_t);
extern void audio_conversate_bounce_phase2_done_58a5a4(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "bounce.anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\bounce_anim.c";
static const char function[] = "bounce_anim_phase1_ready_cb";
static const char invalid[] = "phase1_ready_cb: invalid context";
static const char invalid_compact[] =
    "[bounce.anim]phase1_ready_cb: invalid context";
static const char stopped[] =
    "phase1_ready_cb: animation was stopped, cleaning up";
static const char stopped_compact[] =
    "[bounce.anim]phase1_ready_cb: animation was stopped, cleaning up";
static const char complete[] = "Phase 1 completed, starting phase 2";
static const char complete_compact[] =
    "[bounce.anim]Phase 1 completed, starting phase 2";
static const char started[] = "Phase 2 animation started: duration=%dms";
static const char started_compact[] =
    "[bounce.anim]Phase 2 animation started: duration=%dms";

void audio_conversate_bounce_y_58a3fc(uint32_t object, int32_t y) {
    if (object != 0u) audio_uart_page_43f142(object, y);
}

void audio_conversate_bounce_phase1_done_58a408(const uint8_t *descriptor) {
    volatile uint32_t *const state =
        (volatile uint32_t *)(void *)audio_conversate_bounce_state_20073e14;
    volatile uint32_t *const context =
        (volatile uint32_t *)(uintptr_t)*(const uint32_t *)(const void *)(descriptor + 28u);
    if (context == 0 || context[0] == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x44u, invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, invalid_compact, invalid_compact);
        return;
    }
    if (context != state || state[0] != context[0]) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 0x4au, stopped);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10000000u, stopped_compact, stopped_compact);
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x4eu, complete);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10000000u, complete_compact, complete_compact);
    const int32_t y = (int32_t)state[1];
    const int32_t start = y +
        (audio_conversate_bounce_state_20073e14[8] == 0u ? -30 : 30);
    uint32_t animation[24];
    audio_uart_lv_anim_init_4503d6(animation);
    animation[0] = state[0];
    animation[1] = (uint32_t)(uintptr_t)audio_conversate_bounce_phase2_y_58a598;
    audio_uart_lv_anim_values_4506ce(animation, start, y);
    animation[12] = 200u;
    animation[8] = (uint32_t)(uintptr_t)audio_uart_lv_anim_path_450672;
    animation[4] = (uint32_t)(uintptr_t)audio_conversate_bounce_phase2_done_58a5a4;
    animation[7] = (uint32_t)(uintptr_t)state;
    (void)audio_uart_lv_anim_start_450408(animation);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x67u, started, 200u);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c400000u, started_compact, started_compact, 200u);
}
