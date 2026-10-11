#include <stdint.h>
extern void case_uart_error_dma_matrix(uint8_t *);
extern void case_uart_toidle_dma_branch(uint8_t *);
extern void case_uart_toidle_no_dma_branch(uint8_t *);
extern void case_uart_mixed_tail(uint8_t *);

/* Composed public entry for the evidenced RAM/MMIO fixture domains. Lower
 * DMA abort and TX-completion providers remain explicit link boundaries. */
void case_uart_irq_unified(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr1=uart[0],cr3=uart[2];
    if ((isr&0x80fu)&&((cr3&0x10000001u)||(cr1&0x4000120u))) {
        case_uart_error_dma_matrix(handle);
        return;
    }
    if ((isr&0x20u)&&((cr1&0x20u)||(cr3&0x10000000u))) {
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
