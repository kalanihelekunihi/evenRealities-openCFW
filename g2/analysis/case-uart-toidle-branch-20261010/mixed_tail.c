#include <stdint.h>
extern void case_tx_complete_provider(uint8_t *);

/* Selected no-error/no-IDLE continuation of the public IRQ. */
void case_uart_mixed_tail(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr1=uart[0],cr3=uart[2];
    if ((isr&0x100000u)&&(cr3&0x400000u)) {
        uart[8]=0x100000u; /* fixed-image weak wakeup callback: no-op */
        return;
    }
    if ((isr&0x80u)&&((cr1&0x80u)||(cr3&0x800000u))) {
        void (*tx)(uint8_t *)=*(void (**)(uint8_t *))(void *)(handle+0x78);
        if (tx)tx(handle);
        return;
    }
    if ((isr&0x40u)&&(cr1&0x40u)) {
        uint32_t saved,one=1;
        __asm volatile("mrs %0, primask\nmsr primask, %1": "=&r"(saved):"r"(one):"memory");
        uart[0]&=~0x40u;
        __asm volatile("msr primask, %0"::"r"(saved):"memory");
        *(uint32_t *)(void *)(handle+0x88)=0x20u;
        *(uint32_t *)(void *)(handle+0x78)=0u;
        case_tx_complete_provider(handle);
        return;
    }
    if ((isr&0x800000u)&&(cr1&0x40000000u))return;
    if ((isr&0x1000000u)&&(cr1&0x80000000u))return;
}
