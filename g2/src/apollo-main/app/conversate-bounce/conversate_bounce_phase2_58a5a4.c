/* Apollo Main bounce phase-2 callbacks, native 0x58a598..0x58a67f. */
#include <stdint.h>

extern volatile uint8_t audio_conversate_bounce_state_20073e14[16];
extern void audio_uart_page_43f142(uint32_t, int32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "bounce.anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\bounce_anim.c";
static const char function[] = "bounce_anim_phase2_ready_cb";
static const char invalid[] = "phase2_ready_cb: invalid context";
static const char invalid_compact[] =
    "[bounce.anim]phase2_ready_cb: invalid context";
static const char stopped[] =
    "phase2_ready_cb: animation was stopped, cleaning up";
static const char stopped_compact[] =
    "[bounce.anim]phase2_ready_cb: animation was stopped, cleaning up";
static const char complete[] = "Bounce animation completed";
static const char complete_compact[] =
    "[bounce.anim]Bounce animation completed";

void audio_conversate_bounce_phase2_y_58a598(uint32_t object, int32_t y) {
    if (object != 0u) audio_uart_page_43f142(object, y);
}

void audio_conversate_bounce_phase2_done_58a5a4(const uint8_t *descriptor) {
    volatile uint32_t *const state =
        (volatile uint32_t *)(void *)audio_conversate_bounce_state_20073e14;
    volatile uint32_t *const context =
        (volatile uint32_t *)(uintptr_t)*(const uint32_t *)(const void *)(descriptor + 28u);
    if (context == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x7du, invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, invalid_compact, invalid_compact);
        return;
    }
    if (context != state || state[0] != context[0]) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 0x83u, stopped);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10000000u, stopped_compact, stopped_compact);
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x87u, complete);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c000000u, complete_compact, complete_compact);
    if (state[3] != 0u)
        ((void (*)(const uint8_t *))(uintptr_t)state[3])(descriptor);
    state[0] = 0u;
}
