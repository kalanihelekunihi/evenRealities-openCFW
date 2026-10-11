#include <stdint.h>

/* Selected public IRQ continuation: no enabled error, RX, IDLE or TX flag. */
void case_uart_wakeup_branch(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr3=uart[2];
    if ((isr&0x100000u)&&(cr3&0x400000u)) {
        uart[8]=0x100000u;
        /* Fixed-image weak HAL_UARTEx_WakeupCallback is a no-op. */
    }
}
