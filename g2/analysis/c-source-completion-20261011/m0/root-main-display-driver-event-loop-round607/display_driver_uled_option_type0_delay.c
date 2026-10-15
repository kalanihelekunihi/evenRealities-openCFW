/* Apollo S200 osDelay wrapper at 0x449376. */
#include <stdint.h>

extern uint32_t display_driver_uled_irq_context_44900e(void);
extern void audio_uart_task_delay(uint32_t);

uint32_t display_driver_uled_delay_449376(uint32_t ticks) {
    if (display_driver_uled_irq_context_44900e()!=0u)
        return 0xfffffffau;
    if (ticks!=0u)
        audio_uart_task_delay(ticks);
    return 0u;
}
