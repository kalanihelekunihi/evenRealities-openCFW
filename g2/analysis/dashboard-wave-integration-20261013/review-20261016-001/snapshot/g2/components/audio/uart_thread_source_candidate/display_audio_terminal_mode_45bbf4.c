/* Apollo audio terminal-mode predicate, stock 0x45bbf4..0x45bc04. */
#include <stdint.h>

extern uint32_t audio_settings_terminal_mode(void);

uint32_t audio_uart_display_audio_terminal_mode_45bbf4(void) {
    return audio_settings_terminal_mode() != 0u ? 1u : 0u;
}
