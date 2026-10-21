#include <stdint.h>

/* Selected public-entry domain: ISR.IDLE and CR1.IDLEIE set; no error,
 * RX-ready or DMAR. This is a branch comparison source, not a full IRQ. */
extern void HAL_UARTEx_RxEventCallback(void *, uint16_t);

static void clear_atomic(volatile uint32_t *reg, uint32_t mask)
{
    uint32_t saved, one = 1;
    __asm volatile("mrs %0, primask\nmsr primask, %1"
                   : "=&r"(saved) : "r"(one) : "memory");
    *reg &= ~mask;
    __asm volatile("msr primask, %0" :: "r"(saved) : "memory");
}

void case_uart_toidle_no_dma_branch(uint8_t *handle)
{
    volatile uint32_t *uart = *(volatile uint32_t **)(void *)handle;
    uint32_t isr = uart[7], cr1 = uart[0], cr3 = uart[2];
    if (*(uint32_t *)(void *)(handle + 0x6c) != 1u ||
        !(isr & 0x10u) || !(cr1 & 0x10u) || (cr3 & 0x40u))
        return;
    uart[8] = 0x10u;
    uint16_t size = *(uint16_t *)(void *)(handle + 0x5c);
    uint16_t count = *(uint16_t *)(void *)(handle + 0x5e);
    uint16_t received = (uint16_t)(size - count);
    if (count != 0u && received != 0u) {
        clear_atomic(&uart[0], 0x120u);
        clear_atomic(&uart[2], 0x10000001u);
        *(uint32_t *)(void *)(handle + 0x8c) = 0x20u;
        *(uint32_t *)(void *)(handle + 0x6c) = 0u;
        *(uint32_t *)(void *)(handle + 0x74) = 0u;
        clear_atomic(&uart[0], 0x10u);
        *(uint32_t *)(void *)(handle + 0x70) = 2u;
        HAL_UARTEx_RxEventCallback(handle, received);
    }
}
