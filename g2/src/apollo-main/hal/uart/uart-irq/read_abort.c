/* Source projection of pinned Ambiq read_transaction_abort, stock 0x58dfb2. */
#include <stdint.h>
uint32_t uart_irq_read_abort(void *handle)
{
    volatile uint8_t *s = (volatile uint8_t *)handle;
    uint32_t saved;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(saved) :: "memory");
    uint32_t status;
    if (s[0x11a] == 1u) {
        s[0x11a] = 0;
        for (uint32_t i=0;i<0x38u;i++) s[0x64u+i] = 0;
        *(volatile uint32_t *)(s+0x9c) = 0;
        status = 0;
    } else status = 7;
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
    return status;
}
