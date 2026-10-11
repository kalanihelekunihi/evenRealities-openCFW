/* Stock-corrected projections of three pinned Ambiq UART helpers.
 * Original stock 0x58dd30/5c does not clear bDMABusy: public IRQ service
 * does that unconditionally at 0x58e8e4. Not an archive provider. */
#include <stdint.h>
static volatile uint32_t *uart_regs(uint32_t module)
{
    return (volatile uint32_t *)(0x40039000u + module * 0x1000u);
}
void uart_irq_dma_complete(void *handle)
{
    uint32_t module = *(volatile uint32_t *)((volatile uint8_t *)handle + 0x28);
    volatile uint32_t *r = uart_regs(module);
    r[0x48/4] = 0;
    r[0x04/4] &= ~0x10u;
    r[0x04/4] &= ~0x20u;
}
void uart_irq_dma_abort(void *handle)
{
    uint32_t module = *(volatile uint32_t *)((volatile uint8_t *)handle + 0x28);
    volatile uint32_t *r = uart_regs(module);
    r[0x48/4] = 0;
    r[0x04/4] &= ~0x20u;
    r[0x50/4] &= ~0xfffu;
}
uint32_t uart_irq_get_int_err(uint32_t module, uint32_t status)
{
    volatile uint32_t *r = uart_regs(module);
    status |= r[0x3c/4];
    if (status & 0x40u) return 0x08000006u;
    if (status & 0x80u) return 0x08000007u;
    if (status & 0x100u) return 0x08000008u;
    if (status & 0x200u) return 0x08000009u;
    if (status & 0x400u) return 0x0800000au;
    if (status & 0x1000u) return 0x0800000bu;
    return 0;
}
