#include <stdint.h>

/* Complete native 0x323374..0x3233b0. Native sp+4 is the event pointer;
 * unassigned event bytes remain ambient stack contents. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
uint32_t opencfw_em9305_mode_event_323374(uintptr_t context)
{
    _Alignas(4) uint8_t local[20];
    uint32_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    *(volatile uint8_t *)(local+8u)=0u;
    *(volatile uint16_t *)(void *)(local+6u)=9u;
    int32_t index=(int32_t)((uint32_t)context-base)/912;
    uint8_t value=*(volatile uint8_t *)(context+528u);
    uint16_t first=*(volatile uint16_t *)(context+530u);
    uint16_t second=*(volatile uint16_t *)(context+532u);
    *(volatile uint8_t *)(local+12u)=value;
    *(volatile uint16_t *)(void *)(local+14u)=first;
    *(volatile uint16_t *)(void *)(local+16u)=second;
    *(volatile uint16_t *)(void *)(local+10u)=(uint8_t)index;
    *(volatile uint16_t *)(void *)(local+4u)=(uint8_t)index;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)(local+4u));
}
