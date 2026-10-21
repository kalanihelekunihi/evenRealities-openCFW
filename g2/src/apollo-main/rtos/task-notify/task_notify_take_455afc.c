/* Apollo ulTaskNotifyTakeIndexed 0x455afc..0x455b82.
 * Index zero is the only nonfatal index in this native build. */
#include <stdint.h>

extern void *g2_audio_current_task;                /* RAM 0x20074a20 */
extern void audio_delay_scheduler_assert(void);    /* 0x5fa0a4 */
extern void stock_enter_critical(void);            /* 0x4420d0 */
extern void stock_exit_critical(void);             /* 0x4420e8 */
extern void audio_add_current_to_delayed(uint32_t, uint32_t); /* 0x455fa8 */
extern void audio_yield(void);                     /* 0x4420bc */

uint32_t audio_uart_notify_take_455afc(uint32_t index, int32_t clear_on_exit,
                                        uint32_t wait_ticks) {
    if (index != 0u) {
        audio_delay_scheduler_assert();
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
        for (;;) { }
    }
    stock_enter_critical();
    uint8_t *task = (uint8_t *)g2_audio_current_task;
    uint32_t *value = (uint32_t *)(void *)(task + 0x68u);
    if (*value == 0u) {
        task[0x6cu] = 1u;
        if (wait_ticks != 0u) {
            audio_add_current_to_delayed(wait_ticks, 1u);
            audio_yield();
        }
    }
    stock_exit_critical();
    stock_enter_critical();
    task = (uint8_t *)g2_audio_current_task;
    value = (uint32_t *)(void *)(task + 0x68u);
    uint32_t previous = *value;
    if (previous != 0u) {
        *value = clear_on_exit != 0 ? 0u : previous - 1u;
    }
    task[0x6cu] = 0u;
    stock_exit_critical();
    return previous;
}
