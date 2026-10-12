#include <stdint.h>

/* Native 0x32ce04..0x32ce22. R0 is changed to context+610 and the
 * final STH delay slot executes before returning that address. */
uint32_t opencfw_em9305_init_registered_32ce04(uintptr_t context)
{
    uintptr_t source=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
    uint8_t first=*(volatile uint8_t *)(source+4u);
    *(volatile uint8_t *)(context+609u)=first;
    uint16_t second=*(volatile uint16_t *)(source+8u);
    *(volatile uint16_t *)(context+610u)=second;
    uint16_t third=*(volatile uint16_t *)(source+6u);
    *(volatile uint16_t *)(context+612u)=third;
    return (uint32_t)(context+610u);
}
