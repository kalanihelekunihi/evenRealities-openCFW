/* Native UI-state getter 0x5b16d0..0x5b16d7 and name lookup 0x5b16dc..0x5b16f5. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_state_20071368;
extern const char *audio_conversate_ui_state_names_20000540[];

uint32_t audio_conversate_ui_state_get_5b16d0(void) {
    return audio_conversate_ui_state_20071368;
}

const char *audio_conversate_ui_state_name_5b16dc(uint32_t state) {
    const uint8_t index = (uint8_t)state;
    if (index >= 7u)
        return "UNKNOWN_STATE";
    return audio_conversate_ui_state_names_20000540[index];
}
