#include <stdint.h>
volatile uint32_t case_tx_complete_calls;
volatile uint32_t case_tx_complete_arg;
void case_tx_complete_provider(uint8_t *handle)
{
    case_tx_complete_calls++;
    case_tx_complete_arg=(uint32_t)(uintptr_t)handle;
    *(uint16_t *)(void *)(handle+0x54)^=0x5aa5u;
}
