/* Stock timer transition rules and predicates 0x5b3648..0x5b3765, wrapper 0x5b3d86. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern void audio_conversate_timer_remove_5b36be(uint32_t, uint32_t);
extern const char *audio_conversate_ui_state_name_5b16dc(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

__attribute__((used, section(".g2_conversate_timer_rules_775e6c")))
const uint8_t audio_conversate_timer_rules_775e6c[6][4] = {
    {7u, 1u, 1u, 1u}, {1u, 8u, 1u, 2u},
    {2u, 8u, 2u, 2u}, {8u, 2u, 2u, 1u},
    {2u, 4u, 3u, 1u}, {4u, 2u, 3u, 2u},
};
_Static_assert(sizeof(audio_conversate_timer_rules_775e6c) == 24u,
               "six native four-byte timer rules");

uint32_t audio_conversate_timer_condition_5b3648(uint32_t kind,
                                                   uint32_t first,
                                                   uint32_t second) {
    const uint8_t type = (uint8_t)kind;
    if (type == 7u) return 1u;
    if (type == 8u) return (uint8_t)first != (uint8_t)second;
    return type == (uint8_t)first;
}

uint32_t audio_conversate_timer_rule_match_5b3680(const uint8_t *rule,
                                                    uint32_t old_state,
                                                    uint32_t new_state) {
    if (rule == 0) return 0u;
    if (!audio_conversate_timer_condition_5b3648(rule[0], old_state, new_state))
        return 0u;
    return audio_conversate_timer_condition_5b3648(rule[1], new_state, old_state);
}

uint32_t audio_conversate_timer_change_5b3718(uint32_t old_state,
                                                uint32_t new_state) {
    uint32_t found = 0u;
    for (uint32_t i = 0; i < 6u; ++i) {
        const uint8_t *const rule = audio_conversate_timer_rules_775e6c[i];
        if (audio_conversate_timer_rule_match_5b3680(rule, old_state, new_state)) {
            audio_conversate_timer_remove_5b36be(rule[2], rule[3]);
            found = 1u;
        }
    }
    return found;
}

static const char module[] = "conversate.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c";
static const char function[] = "conversate_timer_mgr_handle_state_transition";
static const char missing[] = "No timer rule found for state transition: %s -> %s";
static const char missing_short[] =
    "[conversate.timer]No timer rule found for state transition: %s -> %s";

void audio_conversate_ui_transition_5b3d86(uint32_t old_state,
                                             uint32_t new_state) {
    if (audio_uart_device_role_get() != 1u)
        return;
    if (audio_conversate_timer_change_5b3718((uint8_t)old_state,
                                               (uint8_t)new_state) != 0u)
        return;
    if (audio_log_flags() & 2u) {
        const char *const next_name = audio_conversate_ui_state_name_5b16dc((uint8_t)new_state);
        const char *const old_name = audio_conversate_ui_state_name_5b16dc((uint8_t)old_state);
        audio_log_extended(4u, module, path, function, 409u, missing,
                           old_name, next_name);
    }
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) {
        const char *const next_name = audio_conversate_ui_state_name_5b16dc((uint8_t)new_state);
        const char *const old_name = audio_conversate_ui_state_name_5b16dc((uint8_t)old_state);
        audio_log_simple(0x10800000u, missing_short, missing_short,
                         old_name, next_name);
    }
}
