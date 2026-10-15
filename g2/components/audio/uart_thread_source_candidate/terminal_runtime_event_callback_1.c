/* Apollo BLE-status callback registered by mode sync, native 0x5e8814. */
#include <stdint.h>
extern void audio_td_notify_state_clear(void);
extern void audio_td_session_struct_clear(void);
extern void audio_terminal_request_runtime_event_if_allowed(uint32_t);

void audio_terminal_runtime_event_callback_1(uint32_t event,const void *payload) {
    if(event!=0u || payload==0) return;
    uint8_t connected=*(const uint8_t *)payload!=0u?1u:0u;
    if(connected==0u) {
        audio_td_notify_state_clear();
        audio_td_session_struct_clear();
    }
    audio_terminal_request_runtime_event_if_allowed(connected);
}
