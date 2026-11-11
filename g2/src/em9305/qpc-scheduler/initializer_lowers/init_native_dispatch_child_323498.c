#include <stdint.h>

/* Native 0x323498..0x3234c2: report a subrate failure (event 0x33) for
 * the connection handle through the LL event callback. The 16-byte event
 * carries the handle at +0 and +6, the status at +3 and +4 and two zero
 * words at +8; byte +5 is not written, as in stock. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

uint32_t opencfw_em9305_dispatch_child_323498(uint32_t handle,uint32_t status)
{
    _Alignas(4) uint8_t event[16];
    *(uint16_t *)(void *)(event+6)=(uint16_t)handle;
    event[4]=(uint8_t)status;
    event[3]=(uint8_t)status;
    *(uint16_t *)(void *)event=(uint16_t)handle;
    *(uint32_t *)(void *)(event+12)=0u;
    *(uint32_t *)(void *)(event+8)=0u;
    event[2]=0x33u;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
