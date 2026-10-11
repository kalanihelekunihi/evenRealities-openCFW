#include <stdint.h>
volatile uint32_t case_tx_calls;
volatile uint32_t case_tx_arg;
volatile uint32_t case_tx_cr1_xor;
volatile uint32_t case_tx_pointer_xor;
void case_tx_ready_callback(uint8_t *handle)
{
    case_tx_calls++;
    case_tx_arg=(uint32_t)(uintptr_t)handle;
    *(uint16_t *)(void *)(handle+0x56)^=0x55aau;
    if (case_tx_cr1_xor) {
        volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
        uart[0]^=case_tx_cr1_xor;
    }
    if (case_tx_pointer_xor)
        *(uint32_t *)(void *)(handle+0x78)^=case_tx_pointer_xor;
}
