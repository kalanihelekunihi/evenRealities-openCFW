/* 0x5ecafa is the already reconstructed unsigned current-session index. */
#include <stdint.h>
extern uint16_t audio_td_current_session_index(void);
uint32_t audio_terminal_display_fallback_5ecafa(void) {
    return audio_td_current_session_index();
}
