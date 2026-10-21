/* Apollo terminal event-name lookup 0x5ea004. */
#include <stdint.h>

extern const char *audio_terminal_event_names[13]; /* native RAM 0x20003e6c */
static const char invalid[]="TERMINAL_EVENT_INVALID"; /* native ROM 0x77c97c */

const char *audio_terminal_event_name_5ea004(uint32_t event) {
    uint32_t id=(uint8_t)event;
    return id<13u?audio_terminal_event_names[id]:invalid;
}
