/* Stock list-animation completion callback 0x58949e and queue processor
 * 0x58956e. */
#include <stdint.h>

extern uint8_t audio_terminal_list_anim_state_base[0xd0];
extern uint32_t g2_flashdb_candidate_tick(void);
extern void audio_terminal_list_anim_old_start_58c6c4(uint32_t, uint32_t,
                                                       uint32_t);
extern void audio_terminal_list_anim_new_start_58c622(uint32_t, uint32_t,
                                                       uint32_t);
extern void audio_terminal_list_anim_new_prepare_5894d6(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "list_anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\list_anim.c";
static const char function[] = "list_anim_play_next";
static const char message[] = "Both old_obj and new_obj are NULL, skip";
static const char short_message[] =
    "[list_anim]Both old_obj and new_obj are NULL, skip";

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_list_anim_state_base + offset);
}

static void store_word(uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(audio_terminal_list_anim_state_base + offset) = value;
}

void audio_terminal_list_anim_process_58956e(void);

void audio_terminal_list_anim_finish_58949e(void) {
    if (audio_terminal_list_anim_state_base[0xc4u] != 0u)
        audio_terminal_list_anim_state_base[0xc4u]--;
    if (audio_terminal_list_anim_state_base[0xc4u] == 0u) {
        audio_terminal_list_anim_state_base[0xc3u] = 0u;
        store_word(0xc8u, 0u);
        store_word(0xccu, 0u);
        audio_terminal_list_anim_process_58956e();
    }
}

__attribute__((noinline)) void audio_terminal_list_anim_process_58956e(void) {
    if (audio_terminal_list_anim_state_base[0xc2u] == 0u ||
        audio_terminal_list_anim_state_base[0xc3u] != 0u)
        return;
    const uint32_t head = audio_terminal_list_anim_state_base[0xc0u];
    const uint32_t old_object = word(head * 12u);
    const uint32_t new_object = word(head * 12u + 4u);
    uint32_t duration = word(head * 12u + 8u);
    audio_terminal_list_anim_state_base[0xc0u] =
        (uint8_t)((head + 1u) % 16u);
    audio_terminal_list_anim_state_base[0xc2u]--;
    if (duration == 0u)
        duration = 200u;
    uint8_t active = (uint8_t)((old_object != 0u) + (new_object != 0u));
    if (active == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0xa4u, message);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u, short_message,
                                        short_message);
        audio_terminal_list_anim_process_58956e();
        return;
    }
    audio_terminal_list_anim_state_base[0xc4u] = active;
    audio_terminal_list_anim_state_base[0xc3u] = 1u;
    store_word(0xc8u, g2_flashdb_candidate_tick());
    store_word(0xccu, duration + 150u);
    const uint32_t finished =
        (uint32_t)(uintptr_t)&audio_terminal_list_anim_finish_58949e;
    if (old_object != 0u)
        audio_terminal_list_anim_old_start_58c6c4(old_object, duration,
                                                   finished);
    if (new_object != 0u) {
        audio_terminal_list_anim_new_start_58c622(new_object, duration,
                                                   finished);
        audio_terminal_list_anim_new_prepare_5894d6(new_object);
    }
}
