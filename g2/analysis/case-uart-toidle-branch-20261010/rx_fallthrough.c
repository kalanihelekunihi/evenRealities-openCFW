#include <stdint.h>
extern void case_uart_mixed_tail(uint8_t *);

/* Selected public-entry domains: no errors with RX-ready, or errors whose
 * interrupt enables are all off. IDLE/TOIDLE remains excluded. */
void case_uart_rx_fallthrough(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr1=uart[0],cr3=uart[2];
    if ((isr&0x80fu)&&((cr3&0x10000001u)||(cr1&0x4000120u)))
        return; /* enabled-error body is a separate isolated candidate */
    if ((isr&0x20u)&&((cr1&0x20u)||(cr3&0x10000000u))) {
        void (*rx)(uint8_t *)=*(void (**)(uint8_t *))(void *)(handle+0x74);
        if (rx)rx(handle);
        return;
    }
    case_uart_mixed_tail(handle);
}
