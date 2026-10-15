/* Apollo Nema color select register, native 0x522a16..0x522a1f. */
#include <stdint.h>

extern void audio_uart_nema_child_514846(uint32_t address, uint32_t value);

void display_driver_nema_select_522a16(uint32_t color)
{
    audio_uart_nema_child_514846(0x12cu, color);
}
