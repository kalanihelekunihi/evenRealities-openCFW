/* Stock Terminal UI FSM state/event name lookups and RAM pointer slots. */
#include <stdint.h>

const char *audio_terminal_ui_state_names[13]
    __attribute__((section(".bss.opencfw.terminal.ui_state_names"), aligned(4), used));
const char *audio_terminal_ui_event_names[40]
    __attribute__((section(".bss.opencfw.terminal.ui_event_names"), aligned(4), used));
_Static_assert(sizeof audio_terminal_ui_state_names == 52u,
               "stock Terminal state-name pointer extent");
_Static_assert(sizeof audio_terminal_ui_event_names == 160u,
               "stock Terminal event-name pointer extent");

static const char unknown_state[] = "UNKNOWN_STATE";
static const char unknown_event[] = "UNKNOWN_EVENT";

const char *audio_terminal_ui_state_name_5e7b10(uint32_t state) {
    uint8_t index = (uint8_t)state;
    return index < 13u ? audio_terminal_ui_state_names[index] : unknown_state;
}

const char *audio_terminal_ui_event_name_5e7b2a(uint32_t event) {
    uint8_t index = (uint8_t)event;
    return index < 40u ? audio_terminal_ui_event_names[index] : unknown_event;
}
