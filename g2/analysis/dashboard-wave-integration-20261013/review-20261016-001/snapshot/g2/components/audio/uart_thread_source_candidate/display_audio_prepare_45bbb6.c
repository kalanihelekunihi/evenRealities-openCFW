/* Apollo audio display preparation, stock 0x45bbb6..0x45bbd0. */
#include <stdint.h>

extern volatile uint32_t audio_uart_display_audio_flag_cell;
extern void audio_uart_display_audio_acquire_45baf0(void);
extern void audio_uart_display_audio_release_45bb58(void);

void audio_uart_display_audio_prepare_45bbb6(void) {
    audio_uart_display_audio_acquire_45baf0();
    if (audio_uart_display_audio_flag_cell == 0u)
        audio_uart_display_audio_flag_cell = 1u;
    audio_uart_display_audio_release_45bb58();
}
