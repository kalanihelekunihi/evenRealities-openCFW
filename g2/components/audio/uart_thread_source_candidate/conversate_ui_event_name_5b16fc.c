/* Native Conversate UI event-name lookup 0x5b16fc..0x5b1715. */
#include <stdint.h>

extern const char *audio_conversate_ui_event_names_20000560[];

const char *audio_conversate_ui_event_name_5b16fc(uint32_t event) {
    const uint8_t index = (uint8_t)event;
    if (index >= 21u)
        return "UNKNOWN_EVENT";
    return audio_conversate_ui_event_names_20000560[index];
}
