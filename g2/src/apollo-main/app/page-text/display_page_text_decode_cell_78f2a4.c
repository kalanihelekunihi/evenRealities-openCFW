/* Apollo ROM callback cell 0x78f2a4: stock value 0x489c5f (Thumb). */
#include <stdint.h>

extern uint32_t audio_uart_text_decode_489c5e(const char *text,
                                               uint32_t *offset);

const uintptr_t audio_uart_text_decode_cell_78f2a4
    __attribute__((section(".g2_rom_78f2a4"), used)) =
        (uintptr_t)&audio_uart_text_decode_489c5e;
