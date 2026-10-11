#include <stdint.h>
volatile uint32_t case_dma_abort_result;
volatile uint32_t case_dma_abort_count;
volatile uint32_t case_dma_abort_argument;
uint32_t case_dma_abort(void *dma)
{
    case_dma_abort_argument=(uint32_t)(uintptr_t)dma;
    case_dma_abort_count++;
    return case_dma_abort_result;
}
