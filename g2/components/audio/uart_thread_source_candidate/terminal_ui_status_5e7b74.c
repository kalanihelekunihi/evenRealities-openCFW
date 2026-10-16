/* Stock Terminal UI FSM dispatcher 0x5e7b74. */
#include <stdint.h>

struct audio_terminal_ui_fsm_cell {
    uint32_t next_state;
    int32_t (*action)(uint32_t old_state, uint32_t event_payload);
};
_Static_assert(sizeof(struct audio_terminal_ui_fsm_cell) == 8u,
               "stock Terminal FSM cell ABI");

extern const struct audio_terminal_ui_fsm_cell audio_terminal_ui_fsm_table[13][40];
extern uint8_t audio_terminal_ui_mode; /* stock 0x2006e345 */
extern const char *audio_terminal_ui_state_name_5e7b10(uint32_t);
extern const char *audio_terminal_ui_event_name_5e7b2a(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] = "terminal_ui_fsm_handler";
static const char event_invalid[] = "terminal ui event invalid: %d";
static const char event_invalid_short[] =
    "[terminal.ui]terminal ui event invalid: %d";
static const char state_invalid[] = "terminal ui state invalid: %d";
static const char state_invalid_short[] =
    "[terminal.ui]terminal ui state invalid: %d";
static const char no_action[] =
    "terminal ui no action: state=%d(%s), event=%d(%s)";
static const char no_action_short[] =
    "[terminal.ui]terminal ui no action: state=%d(%s), event=%d(%s)";
static const char action_failed[] = "terminal ui action failed: event=%d";
static const char action_failed_short[] =
    "[terminal.ui]terminal ui action failed: event=%d";
static const char result_invalid[] =
    "terminal ui action result invalid: event=%d result=%d";
static const char result_invalid_short[] =
    "[terminal.ui]terminal ui action result invalid: event=%d result=%d";
static const char transition[] = "terminal ui state: %d(%s) -> %d(%s)";
static const char transition_short[] =
    "[terminal.ui]terminal ui state: %d(%s) -> %d(%s)";

void audio_terminal_ui_status_5e7b74(uint32_t event_value,
                                     uint32_t event_payload) {
    uint32_t event = (uint8_t)event_value;
    if (event >= 40u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x975u,
                               event_invalid, event);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u, event_invalid_short,
                                        event_invalid_short, event);
        return;
    }
    uint32_t state = audio_terminal_ui_mode;
    if (state >= 13u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x97au,
                               state_invalid, state);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u, state_invalid_short,
                                        state_invalid_short, state);
        return;
    }
    const struct audio_terminal_ui_fsm_cell *cell =
        &audio_terminal_ui_fsm_table[state][event];
    if (cell->action == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x981u, no_action,
                               state, audio_terminal_ui_state_name_5e7b10(state),
                               event, audio_terminal_ui_event_name_5e7b2a(event));
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x09000000u, no_action_short,
                                        no_action_short, state,
                                        audio_terminal_ui_state_name_5e7b10(state),
                                        event, audio_terminal_ui_event_name_5e7b2a(event));
        return;
    }
    uint32_t old_state = state;
    int32_t result = cell->action(state, event_payload);
    if (result == -1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x988u,
                               action_failed, event);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u, action_failed_short,
                                        action_failed_short, event);
        return;
    }
    if (result == 0) {
        audio_terminal_ui_mode = (uint8_t)cell->next_state;
    } else {
        if (result < 1 || (((uint32_t)result + 255u) & 0xffu) > 12u) {
            if (audio_log_flags() & 2u)
                audio_log_extended(1u, module, path, function, 0x991u,
                                   result_invalid, event, result);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compressed_log_output(0x04800000u, result_invalid_short,
                                            result_invalid_short, event, result);
            return;
        }
        audio_terminal_ui_mode = (uint8_t)(result - 1);
    }
    uint32_t new_state = audio_terminal_ui_mode;
    if (old_state != new_state) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 0x997u, transition,
                               old_state, audio_terminal_ui_state_name_5e7b10(old_state),
                               new_state, audio_terminal_ui_state_name_5e7b10(new_state));
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0d000000u, transition_short,
                                        transition_short, old_state,
                                        audio_terminal_ui_state_name_5e7b10(old_state),
                                        new_state,
                                        audio_terminal_ui_state_name_5e7b10(new_state));
    }
}
