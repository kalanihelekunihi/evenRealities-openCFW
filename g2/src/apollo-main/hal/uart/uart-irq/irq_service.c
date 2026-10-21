/* Bounded source projection of pinned Ambiq am_hal_uart_interrupt_service.
 * This file is an oracle candidate, not an admitted archive provider: six
 * child effects still need composed original/source verification. */
#include <stdint.h>

extern void uart_irq_rx_abort(void *);
extern void uart_irq_dma_abort(void *);
extern uint32_t uart_irq_get_int_err(uint32_t, uint32_t);
extern void uart_irq_dma_complete(void *);
extern void uart_irq_read_sm(void *);
extern void uart_irq_write_sm(void *);

uint32_t codec_irq_service(void *handle, uint32_t status)
{
    volatile uint8_t *s = (volatile uint8_t *)handle;
    if (!s || ((*(volatile uint32_t *)s & 0x01ffffffu) != 0x01ea9e06u)) return 2;
    uint32_t module = *(volatile uint32_t *)(s + 0x28);
    if (s[0x11b]) {
        volatile uint32_t *count = *(volatile uint32_t **)(s + 0xe8);
        if (count) {
            uint32_t base = 0x40039000u + module * 0x1000u;
            *count = *(volatile uint32_t *)(s + 0xe4) -
                     (*(volatile uint32_t *)(base + 0x50) & 0xfffu);
        }
        if (status & 0x40u) uart_irq_rx_abort(handle);
        if (status & 0x1000u) uart_irq_dma_abort(handle);
        if (status & 0x800u) {
            void (*callback)(uint32_t, void *) =
                *(void (**)(uint32_t, void *))(s + 0xf0);
            if (callback) {
                callback(uart_irq_get_int_err(module, status),
                         *(void *volatile *)(s + 0xf4));
                *(volatile uint32_t *)(s + 0xf0) = 0;
            }
            uart_irq_dma_complete(handle);
        }
        /* Present in the authenticated stock body after every active pass,
         * including status zero; absent from the pinned upstream function. */
        s[0x11b] = 0;
    } else {
        if (status & 0x50u) uart_irq_read_sm(handle);
        if (status & 0x20u) uart_irq_write_sm(handle);
        if (status & 1u) s[0xde] = 1;
    }
    return 1;
}
