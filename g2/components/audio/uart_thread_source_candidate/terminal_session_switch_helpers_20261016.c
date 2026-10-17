/* Session selector event and root-hide leaves, stock 0x5ed1ec/0x5ed1d6. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_ui_event_5e5484(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_43dfa4(void *,uint32_t);

void audio_terminal_session_switch_event_5ed1ec(uint32_t session) {
    audio_terminal_ui_event_5e5484(4u,session,0u);
}

void audio_terminal_session_root_hide_5ed1d6(void) {
    const uint8_t *p=audio_terminal_ui_state_base;
    uint32_t root=(uint32_t)p[0]|((uint32_t)p[1]<<8)|
                  ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
    if (root!=0u) audio_uart_page_43dfa4((void *)(uintptr_t)root,1u);
}
