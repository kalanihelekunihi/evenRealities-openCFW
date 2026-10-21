/* Apollo MAIN 0x4D403E: nested trace-release and DEMCR status wait. */
#include <stdint.h>

extern uint32_t stock_save_irq(void);
extern uint32_t stock_wait_status(uint32_t budget, uint32_t address,
                                  uint32_t mask, uint32_t expected);

uint32_t stock_trace_disable(void) {
    uint32_t saved = stock_save_irq();
    volatile uint8_t * const users = (volatile uint8_t *)0x20074f5eu;
    if (*users) --*users;
    uint32_t status;
    if (*users) {
        status = 3;
    } else {
        volatile uint32_t * const demcr = (volatile uint32_t *)0xe000edfc;
        *demcr &= ~0x01000000u;
        status = stock_wait_status(10, 0xe000edfc, 0x01000000, 0);
    }
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
    return status;
}
