#include <stdint.h>

/* Native 0x32324c..0x323268: report LL event 0x31 for a handle through
 * the 30e79c callback, as {u16 handle, u16 0x31, u8 handle, u32 value}. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

struct opencfw_em9305_event_31 {
    uint16_t handle;
    uint16_t code;
    uint8_t status;
    uint32_t value;
};

uint32_t opencfw_em9305_dispatch_child_32324c(uint32_t handle, uint32_t value)
{
    struct opencfw_em9305_event_31 event;
    event.value=value;
    event.status=(uint8_t)handle;
    event.handle=(uint16_t)handle;
    event.code=0x31u;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
