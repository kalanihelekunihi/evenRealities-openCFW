/* Bounded stock-corrected projection of pinned Ambiq UART RX abort.
 * FIFO drain, read-transaction abort and delay remain explicit test cuts. */
#include <stdint.h>
extern void uart_irq_dma_abort(void *);
extern uint32_t uart_irq_fifo_drain(void *);
extern uint32_t uart_irq_read_abort(void *);
extern void uart_irq_delay_us(uint32_t);
void uart_irq_rx_abort(void *handle)
{
    volatile uint8_t *s = (volatile uint8_t *)handle;
    uint32_t module = *(volatile uint32_t *)(s+0x28);
    volatile uint32_t *r = (volatile uint32_t *)(0x40039000u + module*0x1000u);
    uint32_t rts = (r[0x30/4] >> 14) & 1u;
    if (rts) { r[0x30/4] &= ~0x4000u; r[0x30/4] &= ~0x800u; }
    r[0x30/4] &= ~0x200u;
    if (r[0x18/4] & 8u) {
        uint32_t baud = *(volatile uint32_t *)(s+0x30);
        uart_irq_delay_us(10000000u / baud + 1u);
    }
    if (s[0x11b]) uart_irq_dma_abort(handle);
    (void)uart_irq_fifo_drain(handle);
    (void)uart_irq_read_abort(handle);
    if (rts) r[0x30/4] |= 0x4000u;
    r[0x30/4] |= 0x200u;
}
