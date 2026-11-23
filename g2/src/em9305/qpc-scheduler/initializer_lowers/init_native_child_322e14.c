#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x322e14..0x322e42: report LL event 12 with status 0 for a 912-byte
 * connection entry, identified by its index in the table at *((uintptr_t)&em9305_ram_805c5c + 0x14u). */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct ll_event_12 {
    uint16_t handle;
    uint16_t code;
    uint8_t status;
    uint8_t reserved;
    uint16_t handle_again;
};

uint32_t opencfw_em9305_child_322e14(uintptr_t entry)
{
    uintptr_t base = em9305_ram_805c5c.u32_805c70;
    struct ll_event_12 event;
    event.status = 0u;
    event.code = 12u;
    uint8_t index = (uint8_t)((int32_t)(entry - base) / 912);
    event.handle_again = index;
    event.handle = index;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
