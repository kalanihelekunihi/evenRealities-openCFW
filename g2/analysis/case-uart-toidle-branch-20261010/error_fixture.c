#include <stdint.h>
volatile uint32_t case_abort_it_result;
volatile uint32_t case_abort_it_count;
volatile uint32_t case_abort_it_argument;
uint32_t case_dma_abort_it(void *dma)
{
    case_abort_it_argument=(uint32_t)(uintptr_t)dma;
    case_abort_it_count++;
    return case_abort_it_result;
}
volatile uint32_t case_rx_mutation;
volatile uint32_t case_rx_cr3_mutation;
volatile uint32_t case_rx_count;
void case_rx_mutate(uint8_t *handle)
{
    uint32_t *error=(uint32_t *)(void *)(handle+0x90);
    *error^=case_rx_mutation;
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    if (case_rx_cr3_mutation)uart[2]^=case_rx_cr3_mutation;
    case_rx_count++;
}
