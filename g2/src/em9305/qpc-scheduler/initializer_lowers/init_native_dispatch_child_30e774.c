#include <stdint.h>

/* Native 0x30e774..0x30e79a: report LL event 0x1c through the 30e79c
 * callback as the packed 9-byte record {u16 handle, u8 0x1c, u8 status,
 * u8 status, u8 handle, u16 value, u8 extra}. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

uint32_t opencfw_em9305_dispatch_child_30e774(uint32_t handle, uint32_t status,
                                              uint32_t value, uint32_t extra)
{
    uint8_t event[12];
    event[5]=(uint8_t)handle;
    *(uint16_t *)&event[0]=(uint16_t)handle;
    event[8]=(uint8_t)extra;
    *(uint16_t *)&event[6]=(uint16_t)value;
    event[4]=(uint8_t)status;
    event[3]=(uint8_t)status;
    event[2]=28u;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
