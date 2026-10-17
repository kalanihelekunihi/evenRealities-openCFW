/* Native 0x5b48f8..0x5b4903: indexed event-name lookup. */
#include <stdint.h>

extern const char *audio_conversate_event_names_200004f4[];

const char *audio_conversate_event_name_5b48f8(uint32_t event) {
    return audio_conversate_event_names_200004f4[(uint8_t)event];
}
