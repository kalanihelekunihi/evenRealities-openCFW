#include <stdint.h>
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

/* Native 0x30e988..0x30e9a0: 8-byte event on the stack (stock frame+4):
 * word 0x001f0000, then the incoming halfword. Bytes 6/7 are not written,
 * as in stock. */
uint32_t opencfw_em9305_init_transition_event_30e988(uint32_t id)
{
    _Alignas(4) uint8_t event[8];
    *(uint32_t *)(void *)event=0x001f0000u;
    *(uint16_t *)(void *)(event+4u)=(uint16_t)id;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
