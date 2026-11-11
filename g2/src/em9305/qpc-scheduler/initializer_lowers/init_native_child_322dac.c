#include <stdint.h>

/* Native 0x322dac..0x322dd6: report LL event 17 for a 912-byte connection
 * entry, identified by its index in the table at *0x805c70. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct ll_event_17 {
    uint16_t handle;
    uint16_t code;
    uint16_t handle_again;
};

uint32_t opencfw_em9305_child_322dac(uintptr_t entry)
{
    uintptr_t base = *(volatile uint32_t *)(uintptr_t)0x805c70u;
    uint8_t index = (uint8_t)((int32_t)(entry - base) / 912);
    struct ll_event_17 event;
    event.code = 17u;
    event.handle_again = index;
    event.handle = index;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
