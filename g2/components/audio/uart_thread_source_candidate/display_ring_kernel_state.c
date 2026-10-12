/* Native CMSIS osKernelGetState at 0x44906c.  Scheduler state is the
 * selected source-backed xTaskGetSchedulerState provider at 0x4558a4. */
#include <stdint.h>
extern uint32_t audio_scheduler_state(void);
extern volatile uint32_t audio_uart_ring_kernel_initialized_20074384;
uint32_t audio_uart_ring_kernel_state(void) {
    uint32_t scheduler=audio_scheduler_state();
    if(scheduler==0u)return 3u;
    if(scheduler==2u)return 2u;
    return audio_uart_ring_kernel_initialized_20074384==1u ? 1u : 0u;
}
