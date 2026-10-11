/* Apollo MAIN 0x455F5E: task notification state clear at index zero. */
#include <stdint.h>

extern uint32_t audio_port_mask_set(void);
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);

uint32_t receiver_state_clear(uint8_t *task, uint32_t index) {
    if (index) {
        (void)audio_port_mask_set();
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0;
        for (;;) __asm__ volatile("b ." ::: "memory");
    }
    if (!task) task = *(uint8_t * volatile *)0x20074a20u;
    stock_enter_critical();
    uint32_t was_received = task[index + 0x6cu] == 2u;
    if (was_received) task[index + 0x6cu] = 0;
    stock_exit_critical();
    return was_received;
}
