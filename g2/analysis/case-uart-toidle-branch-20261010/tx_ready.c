#include <stdint.h>

/* Selected public IRQ continuation with no enabled error, IDLE or wakeup. */
void case_uart_tx_ready_branch(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr1=uart[0],cr3=uart[2];
    if ((isr&0x80u)&&((cr1&0x80u)||(cr3&0x800000u))) {
        void (*tx)(uint8_t *)=*(void (**)(uint8_t *))(void *)(handle+0x78);
        if (tx)tx(handle);
    }
}
