#include <stdint.h>

/* Selected quiet public IRQ continuation through stock 0x0800620e..0x622c. */
void case_uart_fifo_branch(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr1=uart[0];
    if ((isr&0x800000u)&&(cr1&0x40000000u)) {
        /* Fixed-image weak HAL_UARTEx_TxFifoEmptyCallback is a no-op. */
        return;
    }
    if ((isr&0x1000000u)&&(cr1&0x80000000u)) {
        /* Fixed-image weak HAL_UARTEx_RxFifoFullCallback is a no-op. */
        return;
    }
}
