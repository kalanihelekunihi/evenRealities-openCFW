#include <stdint.h>

/* Native 0x323574..0x323592: report LL event 0x2d for a handle, carrying
 * the handle low byte and a status byte. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct ll_event_2d {
    uint16_t handle;
    uint16_t code;
    uint8_t handle_low;
    uint8_t status;
};

uint32_t opencfw_em9305_dispatch_child_323574(uint32_t handle, uint32_t status)
{
    struct ll_event_2d event;
    event.handle = (uint16_t)handle;
    event.code = 0x2du;
    event.handle_low = (uint8_t)handle;
    event.status = (uint8_t)status;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
