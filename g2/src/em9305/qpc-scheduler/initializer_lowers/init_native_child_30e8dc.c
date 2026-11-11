#include <stdint.h>

/* Native 0x30e8dc..0x30e910: post LL event 26 for a handle: status and
 * reason bytes followed by a six-byte address built from {low,high}. */
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct init_event_30e8dc {
    uint16_t handle;
    uint16_t event;
    uint8_t status;
    uint8_t reason;
    uint16_t address[3];
};

uint32_t opencfw_em9305_child_30e8dc(uint32_t handle,uint32_t reason,
                                     uint32_t low,uint32_t high)
{
    struct init_event_30e8dc message;
    message.reason=(uint8_t)reason;
    message.status=(uint8_t)handle;
    message.handle=(uint16_t)handle;
    message.event=26u;
    message.address[0]=0u;
    message.address[1]=0u;
    message.address[2]=0u;
    (void)opencfw_em9305_radio_address_write_3045e8((uintptr_t)message.address,low,high);
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&message);
}
