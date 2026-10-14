/* Apollo NEMA mode lower calls at 0x5226d6, 0x52294c, 0x4b1588. */
#include <stdint.h>
extern void audio_uart_nema_child_514846(uint32_t,uint32_t); /* selected */
extern volatile uint32_t audio_uart_nema_context_cell[1]; /* selected */

void display_driver_nema_mode_control_5226d6(uint32_t enabled) {
    audio_uart_nema_child_514846(0x118u,enabled!=0u?0x90000000u:0u);
}
void display_driver_nema_mode_commit_52294c(uint32_t value) {
    audio_uart_nema_child_514846(0x11cu,value);
}
void display_driver_gpu_mode_mask_4b1588(uint32_t enabled) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    uint32_t mask=enabled!=0u?0x08000000u:0u;
    context[0x14u/4u]=mask;
    context[0x18u/4u]=context[0x0cu/4u]|context[0x10u/4u]|
                       context[0x1cu/4u]|mask;
}
