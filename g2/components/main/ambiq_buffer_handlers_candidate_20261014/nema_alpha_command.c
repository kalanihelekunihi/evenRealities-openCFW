/* Apollo Nema alpha command at native 0x522960. */
#include <stdint.h>
extern void audio_uart_nema_child_514846(uint32_t,uint32_t);
void audio_uart_nema_alpha_command_522960(uint32_t alpha) {
    audio_uart_nema_child_514846(0x1d8u,alpha);
}
