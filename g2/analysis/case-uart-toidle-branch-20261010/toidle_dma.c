#include <stdint.h>

extern void HAL_UARTEx_RxEventCallback(void *, uint16_t);
extern uint32_t case_dma_abort(void *);

static void clear_atomic(volatile uint32_t *reg, uint32_t mask)
{
    uint32_t saved, one = 1;
    __asm volatile("mrs %0, primask\nmsr primask, %1"
                   : "=&r"(saved) : "r"(one) : "memory");
    *reg &= ~mask;
    __asm volatile("msr primask, %0" :: "r"(saved) : "memory");
}

/* Selected public-entry domain: TOIDLE, IDLE flag/enable, DMAR set,
 * no error or RX-ready flags. DMA abort remains a test provider boundary. */
void case_uart_toidle_dma_branch(uint8_t *handle)
{
    volatile uint32_t *uart = *(volatile uint32_t **)(void *)handle;
    uint32_t isr = uart[7], cr1 = uart[0], cr3 = uart[2];
    if (*(uint32_t *)(void *)(handle + 0x6c) != 1u ||
        !(isr & 0x10u) || !(cr1 & 0x10u) || !(cr3 & 0x40u))
        return;
    uart[8] = 0x10u;
    uint8_t *dma = *(uint8_t **)(void *)(handle + 0x80);
    volatile uint32_t *channel = *(volatile uint32_t **)(void *)dma;
    uint16_t remaining = (uint16_t)channel[1];
    uint16_t size = *(uint16_t *)(void *)(handle + 0x5c);
    if (remaining == 0u)
        return;
    if (remaining < size) {
        *(uint16_t *)(void *)(handle + 0x5e) = remaining;
        if (!(channel[0] & 0x20u)) {
            clear_atomic(&uart[0], 0x100u);
            clear_atomic(&uart[2], 1u);
            clear_atomic(&uart[2], 0x40u);
            *(uint32_t *)(void *)(handle + 0x8c) = 0x20u;
            *(uint32_t *)(void *)(handle + 0x6c) = 0u;
            clear_atomic(&uart[0], 0x10u);
            (void)case_dma_abort(dma);
        }
        *(uint32_t *)(void *)(handle + 0x70) = 2u;
        HAL_UARTEx_RxEventCallback(handle, (uint16_t)(size - remaining));
    }
}
