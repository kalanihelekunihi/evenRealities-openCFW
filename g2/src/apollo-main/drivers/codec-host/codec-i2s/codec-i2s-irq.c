#include <stdint.h>

/* Stock __NVIC_SetPriority 0x57a4b0 and __NVIC_EnableIRQ 0x57a46c.
 * NVIC address literals are architectural registers, not product data. */
void g2_codec_irq_priority(int32_t irq, uint32_t priority) {
    int16_t number = (int16_t)irq;
    uintptr_t address;
    if (number < 0)
        address = 0xe000ed18u - 4u + ((uint16_t)number & 15u);
    else
        address = 0xe000e400u + (uint16_t)number;
    *(volatile uint8_t *)address = (uint8_t)(priority << 4);
}

void g2_codec_irq_enable(int32_t irq) {
    int16_t number = (int16_t)irq;
    if (number >= 0) {
        volatile uint32_t *const set_enable = (volatile uint32_t *)(uintptr_t)0xe000e100u;
        set_enable[(uint16_t)number >> 5] = 1u << ((uint16_t)number & 31u);
    }
}

/* Stock 0x473934: MRS R0,PRIMASK; CPSIE I; BX LR. */
uint32_t g2_codec_global_irq_enable(void) {
    uint32_t prior;
    __asm volatile("mrs %0, primask\n\tcpsie i" : "=r"(prior) : : "memory");
    return prior;
}
