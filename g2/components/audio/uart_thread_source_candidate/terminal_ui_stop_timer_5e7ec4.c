/* Stock 0x5e7ec4: clear the terminal timer's 24-byte RAM context. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);

uint8_t audio_terminal_ui_timer_state_20073c38[0x18]
    __attribute__((section(".bss.opencfw.terminal.ui_timer"), aligned(4), used));
_Static_assert(sizeof audio_terminal_ui_timer_state_20073c38 == 0x18u,
               "stock terminal timer clear extent");

void audio_terminal_ui_stop_timer_5e7ec4(void) {
    audio_uart_buffer_zero(audio_terminal_ui_timer_state_20073c38, 0x18u, 0u);
}
