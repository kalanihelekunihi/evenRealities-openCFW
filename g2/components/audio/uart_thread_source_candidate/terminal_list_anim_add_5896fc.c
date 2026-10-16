/* Stock list-animation elapsed, timeout recovery and queue add at
 * 0x5893f0/0x5893fe/0x5896fc. */
#include <stdint.h>

extern uint8_t audio_terminal_list_anim_state_base[0xd0];
extern uint32_t g2_flashdb_candidate_tick(void);
extern void audio_terminal_list_anim_init_58966c(void);
extern void audio_terminal_list_anim_process_58956e(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "list_anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\list_anim.c";
static const char recover_function[] = "list_anim_try_recover_timeout";
static const char add_function[] = "list_anim_add";
static const char timeout_message[] =
    "Animation timed out, elapsed=%lu ms, timeout=%lu ms, pending=%u";
static const char timeout_short[] =
    "[list_anim]Animation timed out, elapsed=%lu ms, timeout=%lu ms, pending=%u";
static const char full_message[] = "Animation queue is full";
static const char full_short[] = "[list_anim]Animation queue is full";
static const char null_message[] = "Both old_obj and new_obj are NULL";
static const char null_short[] = "[list_anim]Both old_obj and new_obj are NULL";

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_list_anim_state_base + offset);
}

static void store_word(uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(audio_terminal_list_anim_state_base + offset) = value;
}

__attribute__((noinline)) uint32_t audio_terminal_list_anim_elapsed_5893f0(
    uint32_t start_tick) {
    return g2_flashdb_candidate_tick() - start_tick;
}

__attribute__((noinline)) void audio_terminal_list_anim_timeout_poll_5893fe(void) {
    if (audio_terminal_list_anim_state_base[0xc3u] == 0u ||
        word(0xccu) == 0u)
        return;
    if (audio_terminal_list_anim_elapsed_5893f0(word(0xc8u)) <= word(0xccu))
        return;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, recover_function, 0x3du,
                           timeout_message,
                           audio_terminal_list_anim_elapsed_5893f0(word(0xc8u)),
                           word(0xccu), audio_terminal_list_anim_state_base[0xc4u]);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(
            0x08c00000u, timeout_short, timeout_short,
            audio_terminal_list_anim_elapsed_5893f0(word(0xc8u)),
            word(0xccu), audio_terminal_list_anim_state_base[0xc4u]);
    audio_terminal_list_anim_init_58966c();
}

uint32_t audio_terminal_session_animate_5896fc(uint32_t old_object,
                                                 uint32_t new_object,
                                                 uint32_t duration) {
    audio_terminal_list_anim_timeout_poll_5893fe();
    if (audio_terminal_list_anim_state_base[0xc2u] >= 16u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, add_function, 0xeau,
                               full_message);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u, full_short, full_short);
        return 0u;
    }
    if (old_object == 0u && new_object == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, add_function, 0xf0u,
                               null_message);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u, null_short, null_short);
        return 0u;
    }
    const uint32_t tail = audio_terminal_list_anim_state_base[0xc1u];
    store_word(tail * 12u, old_object);
    store_word(tail * 12u + 4u, new_object);
    store_word(tail * 12u + 8u, duration);
    audio_terminal_list_anim_state_base[0xc1u] = (uint8_t)((tail + 1u) % 16u);
    audio_terminal_list_anim_state_base[0xc2u]++;
    if (audio_terminal_list_anim_state_base[0xc3u] == 0u)
        audio_terminal_list_anim_process_58956e();
    return 1u;
}
