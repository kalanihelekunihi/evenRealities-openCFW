#include <stdint.h>
extern void case_uart_toidle_dma_branch(uint8_t *);
extern void case_uart_toidle_no_dma_branch(uint8_t *);
extern void case_uart_mixed_tail(uint8_t *);
extern uint32_t case_dma_abort_it(void *);

static void clear_atomic(volatile uint32_t *reg,uint32_t mask)
{
    uint32_t saved,one=1;
    __asm volatile("mrs %0, primask\nmsr primask, %1": "=&r"(saved):"r"(one):"memory");
    *reg&=~mask;
    __asm volatile("msr primask, %0"::"r"(saved):"memory");
}

void case_uart_dma_abort_callback(uint8_t *dma)
{
    uint8_t *handle=*(uint8_t **)(void *)(dma+0x28);
    *(uint16_t *)(void *)(handle+0x5e)=0;
    *(uint16_t *)(void *)(handle+0x56)=0;
    /* Fixed-image weak error callback has no observable effect. */
}

/* Called only after case_uart_error_irq has executed EndRxTransfer. */
void case_uart_dma_boundary(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    clear_atomic(&uart[2],0x40u);
    uint8_t *dma=*(uint8_t **)(void *)(handle+0x80);
    if (!dma)return;
    *(void (**)(uint8_t *))(void *)(dma+0x38)=case_uart_dma_abort_callback;
    if (case_dma_abort_it(dma)!=0u)
        (*(void (**)(uint8_t *))(void *)(dma+0x38))(dma);
}

/* Called after the source RX/error prefix's nonreturning checks. */
void case_uart_other_irq(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr1=uart[0];
    if ((isr&0x20u)&&((cr1&0x20u)||(uart[2]&0x10000000u))) {
        void (*rx)(uint8_t *)=*(void (**)(uint8_t *))(void *)(handle+0x74);
        if (rx)rx(handle);
        return;
    }
    if (*(uint32_t *)(void *)(handle+0x6c)==1u &&
        (isr&0x10u)&&(cr1&0x10u)) {
        if (uart[2]&0x40u)case_uart_toidle_dma_branch(handle);
        else case_uart_toidle_no_dma_branch(handle);
        return;
    }
    case_uart_mixed_tail(handle);
}
