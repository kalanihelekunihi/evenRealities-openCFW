/* Native Conversate UI action dispatcher 0x5b1724..0x5b198b. */
#include <stdint.h>

typedef uint32_t (*audio_conversate_ui_action_handler)(uint32_t, uint32_t);
typedef struct {
    uint8_t next_state;
    uint8_t reserved[3];
    audio_conversate_ui_action_handler handler;
} audio_conversate_ui_route;

extern const audio_conversate_ui_route audio_conversate_ui_action_matrix_686920[7][21];
extern uint8_t audio_conversate_ui_state_20071368;
extern const char *audio_conversate_ui_event_name_5b16fc(uint32_t);
extern const char *audio_conversate_ui_state_name_5b16dc(uint32_t);
extern void audio_conversate_ui_transition_5b3d86(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

_Static_assert(sizeof(audio_conversate_ui_route) == 8u, "stock route width");
static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] = "conversate_ui_fsm_handler";
static const char bad_event[] = "UI event is invalid: %d";
static const char bad_event_short[] = "[conversate.ui]UI event is invalid: %d";
static const char event_message[] = "UI event [%d|%s]";
static const char event_short[] = "[conversate.ui]UI event [%d|%s]";
static const char bad_state[] = "UI current state is invalid: %d";
static const char bad_state_short[] = "[conversate.ui]UI current state is invalid: %d";
static const char no_route[] =
    "UI current state[%d|%s] no match action for event[%d|%s]";
static const char no_route_short[] =
    "[conversate.ui]UI current state[%d|%s] no match action for event[%d|%s]";
static const char transition[] = "UI state [%d|%s] -> [%d|%s]";
static const char transition_short[] =
    "[conversate.ui]UI state [%d|%s] -> [%d|%s]";
static const char failed[] = "UI transition action failed";
static const char failed_short[] = "[conversate.ui]UI transition action failed";

void audio_conversate_ui_action_5b1724(uint32_t event, uint32_t value) {
    const uint8_t id = (uint8_t)event;
    if (id >= 21u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 586u,
                               bad_event, id);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, bad_event_short, bad_event_short, id);
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 590u,
                           event_message, id, audio_conversate_ui_event_name_5b16fc(id));
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c800000u, event_short, event_short, id,
                         audio_conversate_ui_event_name_5b16fc(id));
    const uint8_t state = audio_conversate_ui_state_20071368;
    if (state >= 7u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 593u,
                               bad_state, state);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, bad_state_short, bad_state_short, state);
        return;
    }
    const audio_conversate_ui_route *const route =
        &audio_conversate_ui_action_matrix_686920[state][id];
    if (route->handler == 0) {
        if (audio_log_flags() & 2u) {
            const char *const event_name = audio_conversate_ui_event_name_5b16fc(id);
            const char *const state_name = audio_conversate_ui_state_name_5b16dc(state);
            audio_log_extended(2u, module, path, function, 601u, no_route,
                               state, state_name, id, event_name);
        }
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) {
            const char *const event_name = audio_conversate_ui_event_name_5b16fc(id);
            const char *const state_name = audio_conversate_ui_state_name_5b16dc(state);
            audio_log_simple(0x09000000u, no_route_short, no_route_short,
                             state, state_name, id, event_name);
        }
        return;
    }
    if (route->handler(state, value) != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 616u, failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, failed_short, failed_short);
        return;
    }
    const uint8_t next = route->next_state;
    if (state != next) {
        if (audio_log_flags() & 2u) {
            const char *const next_name = audio_conversate_ui_state_name_5b16dc(next);
            const char *const state_name = audio_conversate_ui_state_name_5b16dc(state);
            audio_log_extended(3u, module, path, function, 611u, transition,
                               state, state_name, next, next_name);
        }
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) {
            const char *const next_name = audio_conversate_ui_state_name_5b16dc(next);
            const char *const state_name = audio_conversate_ui_state_name_5b16dc(state);
            audio_log_simple(0x0d000000u, transition_short, transition_short,
                             state, state_name, next, next_name);
        }
    }
    audio_conversate_ui_state_20071368 = next;
    audio_conversate_ui_transition_5b3d86(state, next);
}
