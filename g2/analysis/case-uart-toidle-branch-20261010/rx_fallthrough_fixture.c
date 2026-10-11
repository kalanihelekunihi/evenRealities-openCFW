#include <stdint.h>
volatile uint32_t case_rx_tail_calls;
volatile uint32_t case_rx_tail_arg;
volatile uint32_t case_rx_tail_mutation;
void case_rx_tail_callback(uint8_t *handle)
{
    case_rx_tail_calls++;
    case_rx_tail_arg=(uint32_t)(uintptr_t)handle;
    if (case_rx_tail_mutation) {
        volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
        uart[0]^=0x40u;
        uart[2]^=0x400000u;
        *(uint32_t *)(void *)(handle+0x74)^=0x100u;
        *(uint16_t *)(void *)(handle+0x5e)^=0x55aau;
    }
}
