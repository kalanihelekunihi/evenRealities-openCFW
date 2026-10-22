/* Apollo display-driver wrappers 0x473abc, 0x473ac6, 0x473b34, 0x473b46. */
#include <stdint.h>
extern uint32_t audio_uart_ring_state_transition_4c9b86(uint32_t);
extern uint32_t audio_uart_ring_resource_transition_4c9be2(uint32_t);
extern int32_t osTimerStart(void *, uint32_t);
extern int32_t audio_timer_stop(void *);
void * volatile display_driver_timer_handle; /* source-owned BSS cell; SRAM 0x200744f0 */

void display_driver_init_473abc(void) {
    (void)audio_uart_ring_state_transition_4c9b86(12u);
}
void display_driver_init_473ac6(void) {
    (void)audio_uart_ring_resource_transition_4c9be2(12u);
}
/* Stock 0x473B34 (display_driver_timer_start_473b34) */
void display_driver_case1_b(void) {
    (void)osTimerStart(display_driver_timer_handle, 2000u);
}
/* Stock 0x473B46 (display_driver_timer_stop_473b46) */
void display_driver_case5_a(void) {
    (void)audio_timer_stop(display_driver_timer_handle);
}
