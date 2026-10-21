/* Apollo Main Conversate list-view mode and immediate-state helpers. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_terminal_ui_object_valid_43e2ea(uint32_t);
extern void audio_conversate_list_slot_alpha_5b0c72(uint32_t, uint32_t);
extern void audio_conversate_list_slot_fade_5b0ca0(uint32_t, uint32_t, uint32_t,
                                                     uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] = "conversate_ui_list_view_mode_set";
static const char invalid[] = "Invalid list view mode: %d";
static const char invalid_compact[] = "[conversate.ui]Invalid list view mode: %d";
static const char default_reason[] = "none";
static const char success[] = "List view mode -> %d, reason: %s";
static const char success_compact[] =
    "[conversate.ui]List view mode -> %d, reason: %s";

static volatile uint8_t *ui_state(void) {
    return (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
}
static uint32_t word(const volatile uint8_t *state, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(state + offset);
}

uint32_t audio_conversate_list_view_mode_rank_5b0c30(uint32_t mode) {
    switch ((uint8_t)mode) {
    case 0u: return 0u;
    case 1u: return 1u;
    case 2u: return 4u;
    default: return 0u;
    }
}

void audio_conversate_list_view_apply_5b0d24(uint32_t ignored_state,
                                               uint32_t mode) {
    const volatile uint8_t *const state =
        (const volatile uint8_t *)(uintptr_t)ignored_state;
    const uint8_t rank = (uint8_t)audio_conversate_list_view_mode_rank_5b0c30(mode);
    for (uint32_t slot = 0u; slot < 4u; ++slot) {
        const uint32_t object = word(state, 0x6cu + slot * 4u);
        if (object != 0u && audio_terminal_ui_object_valid_43e2ea(object) != 0u)
            audio_conversate_list_slot_alpha_5b0c72(object, slot < rank ? 0u : 255u);
    }
}

void audio_conversate_ui_list_view_mode_set_5b0edc(
    uint32_t mode, uint32_t animate, const char *reason) {
    volatile uint8_t *const state = ui_state();
    if (word(state, 0x64u) == 0u) return;
    const uint8_t next = (uint8_t)mode;
    if (next >= 3u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x100u, invalid, next);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08400000u,
                                        invalid_compact, invalid_compact, next);
        return;
    }
    const uint8_t old_rank =
        (uint8_t)audio_conversate_list_view_mode_rank_5b0c30(state[0x97u]);
    const uint8_t new_rank = (uint8_t)audio_conversate_list_view_mode_rank_5b0c30(next);
    if ((uint8_t)animate == 0u) {
        audio_conversate_list_view_apply_5b0d24((uint32_t)(uintptr_t)state, next);
    } else if (old_rank < new_rank) {
        for (uint32_t slot = old_rank; slot < new_rank && slot < 4u; ++slot)
            audio_conversate_list_slot_fade_5b0ca0(
                word(state, 0x6cu + slot * 4u), 255u, 0u,
                (slot - old_rank) * 50u, 300u);
    } else {
        uint32_t ordinal = 0u;
        for (int32_t slot = (int32_t)old_rank - 1; slot >= (int32_t)new_rank; --slot)
            audio_conversate_list_slot_fade_5b0ca0(
                word(state, 0x6cu + (uint32_t)slot * 4u), 0u, 255u,
                ordinal++ * 50u, 300u);
    }
    state[0x97u] = next;
    const char *const why = reason != 0 ? reason : default_reason;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x11bu, success, next, why);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c800000u,
                                    success_compact, success_compact, next, why);
}
