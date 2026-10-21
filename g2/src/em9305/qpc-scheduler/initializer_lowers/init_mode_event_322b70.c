#include <stdint.h>

/* Native 0x322b70..0x322baa. Slot table 0x8027e0 is a runtime data
 * contract; its callback receives context in R0 and literal zero in R1. */
extern uint32_t opencfw_em9305_mode_event_313338(uintptr_t field);
uint32_t opencfw_em9305_mode_event_322b70(uintptr_t context)
{
    uint32_t config=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
    uint32_t selector=*(volatile uint8_t *)(uintptr_t)(config+53u);
    *(volatile uint8_t *)(context+321u)=(uint8_t)selector;
    uint32_t value=*(volatile uint8_t *)(uintptr_t)(config+54u);
    *(volatile uint8_t *)(context+77u)=(uint8_t)value;
    *(volatile uint8_t *)(context+76u)=(uint8_t)value;
    uintptr_t callback=*(volatile uint32_t *)(uintptr_t)(0x8027e0u+4u*selector);
    uint32_t result=((uint32_t (*)(uintptr_t,uint32_t))callback)(context,0u);
    *(volatile uint8_t *)(context+65u)=(uint8_t)result;
    return opencfw_em9305_mode_event_313338(context+16u);
}
