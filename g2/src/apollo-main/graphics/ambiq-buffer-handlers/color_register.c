/* Apollo Ambiq Nema color register selector at 0x4b1474..0x4b1486. */
#include <stdint.h>

extern uint32_t audio_uart_nema_child_514846(uint32_t,uint32_t);

uint32_t audio_uart_ambiq_color_register_4b1474(uint32_t index,
                                                   uint32_t color) {
    const uint32_t address=(index<<2)+0x200u;
    if (address<0x20du) return audio_uart_nema_child_514846(address,color);
    return address;
}
