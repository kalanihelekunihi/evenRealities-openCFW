/* Session selector's two small children at 0x5eca44 and 0x5ed1fa. */
#include <stdint.h>
extern void audio_terminal_ui_event_5e5484(uint32_t,uint32_t,uint32_t);

int32_t audio_terminal_session_index_i16_5eca44(uint32_t raw) {
    return (int16_t)raw;
}
void audio_terminal_session_list_event_5ed1fa(void) {
    audio_terminal_ui_event_5e5484(2u,0u,0u);
}
