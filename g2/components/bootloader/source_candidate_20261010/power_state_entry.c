/* Deep-sleep BL to stock 0x41cd1a, selected nullable power callback wrapper. */
#include <stdint.h>
__attribute__((naked)) void power_state(uint32_t stimulus, uint32_t on, uint8_t *args)
{
    __asm__ volatile("b.w power_state_wrapper");
}
