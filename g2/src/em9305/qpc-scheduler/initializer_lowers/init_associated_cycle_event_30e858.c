#include <stdint.h>

/* Native 0x30e858..0x30e876: report LL event 0x35 through the 30e79c
 * callback as {u16 0, u8 0x35, u8 0, u8 handle, u8 status, u8 count}. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

uint32_t opencfw_em9305_associated_cycle_event_30e858(uint32_t handle, uint32_t status,
                                                      uint32_t count)
{
    volatile struct {
        uint32_t prefix;
        uint8_t handle;
        uint8_t status;
        uint8_t count;
        uint8_t unused;
    } event;
    event.handle=(uint8_t)handle;
    event.prefix=0x35u<<16;
    event.count=(uint8_t)count;
    event.status=(uint8_t)status;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
