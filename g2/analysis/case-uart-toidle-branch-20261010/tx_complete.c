#include <stdint.h>
extern void case_tx_complete_provider(uint8_t *);

/* Selected quiet public IRQ continuation through stock 0x080061e0..0x620c. */
void case_uart_tx_complete_branch(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr1=uart[0];
    if ((isr&0x40u)&&(cr1&0x40u)) {
        uint32_t saved,one=1;
        __asm volatile("mrs %0, primask\nmsr primask, %1"
                       : "=&r"(saved):"r"(one):"memory");
        uart[0]&=~0x40u;
        __asm volatile("msr primask, %0"::"r"(saved):"memory");
        *(uint32_t *)(void *)(handle+0x88)=0x20u;
        *(uint32_t *)(void *)(handle+0x78)=0u;
        case_tx_complete_provider(handle);
    }
}
