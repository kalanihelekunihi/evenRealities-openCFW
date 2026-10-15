/* Native terminal agent event-token helpers 0x5e5166 and 0x5e51b0. */
#include <stdint.h>

void *audio_terminal_agent_session_ptr
    __attribute__((section(".g2.ram.terminal_agent_session_ptr"),used,aligned(4))); /* RAM 0x2006e0d4 */
uint8_t audio_terminal_agent_special_flag
    __attribute__((section(".g2.ram.terminal_agent_special_flag"),used)); /* RAM 0x2006e35c */
extern int32_t audio_uart_lv_obj_y_44e498(void *);

uint32_t audio_terminal_agent_text_token(uint8_t kind, uint16_t length) {
    uint32_t scroll = 0u;
    if (audio_terminal_agent_session_ptr != 0) {
        int32_t y = audio_uart_lv_obj_y_44e498(audio_terminal_agent_session_ptr);
        if (y >= 0) scroll = (uint32_t)y;
    }
    return ((uint32_t)(kind & 15u) << 20) |
           ((uint32_t)(length & 63u) << 24) |
           (audio_terminal_agent_special_flag != 0u ? 0x40000000u : 0u) |
           (scroll & 0xffffu);
}

uint32_t audio_terminal_agent_trigger_token(uint32_t flags, uint32_t tick) {
    return (flags & 15u) | (tick << 4);
}
