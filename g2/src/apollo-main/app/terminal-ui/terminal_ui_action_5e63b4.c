/* Stock Terminal FSM event-word action at 0x5e63b4. */
#include <stdint.h>

extern void audio_terminal_event_emit_5eadd4(uint32_t kind,
                                              uint32_t event,
                                              const void *message);

struct terminal_event_message {
    uint8_t present;
    uint8_t upper_flag;
    uint8_t reserved[2];
    uint32_t low_word;
};
_Static_assert(sizeof(struct terminal_event_message) == 8u,
               "stock event message extent");

int32_t audio_terminal_ui_action_5e63b4(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    uint32_t kind = (event_payload >> 20) & 15u;
    uint32_t event = (event_payload >> 24) & 63u;
    struct terminal_event_message message = {
        1u, (uint8_t)((event_payload >> 30) & 1u), {0u, 0u},
        (uint16_t)event_payload
    };
    if (kind != 0u)
        audio_terminal_event_emit_5eadd4(kind, event, &message);
    return 0;
}
