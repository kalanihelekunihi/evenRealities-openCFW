#include <stdint.h>

/* Native return-delay slot stores at 0x32cb40 and 0x32cf78. */
uint32_t opencfw_em9305_mode_event_32cb40(uintptr_t context)
{
    *(volatile uint8_t *)(context+12u)=0x3du;
    return (uint32_t)context;
}

uint32_t opencfw_em9305_mode_event_32cf78(uintptr_t context)
{
    *(volatile uint8_t *)(context+12u)=0xffu;
    return (uint32_t)context;
}
