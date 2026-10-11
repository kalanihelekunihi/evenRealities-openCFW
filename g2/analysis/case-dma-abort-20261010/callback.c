#include <stdint.h>
volatile uint32_t case_abort_callback_count;
volatile uint32_t case_abort_callback_arg;
void case_abort_callback(void *dma)
{
    case_abort_callback_count++;
    case_abort_callback_arg=(uint32_t)(uintptr_t)dma;
    *(uint32_t *)(void *)((uint8_t *)dma+0x30)^=0x5aa55aa5u;
}
