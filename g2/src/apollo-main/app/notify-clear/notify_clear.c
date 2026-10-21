/* Native task-notification-state clear 0x455f5e. Index zero only, as
 * authenticated by the native body; nonzero index takes its fatal path. */
#include <stdint.h>
extern void offline_assert(void) __attribute__((noreturn));
extern void *receiver_current_task(void);
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);

uint32_t audio_uart_wait_clear(void *task, uint32_t index) {
    if (index != 0u) offline_assert();
    if (task == 0) task = receiver_current_task();
    stock_enter_critical();
    uint8_t *state = (uint8_t *)task + 0x6cu;
    uint32_t was_received = *state == 2u;
    if (was_received) *state = 0u;
    stock_exit_critical();
    return was_received;
}
