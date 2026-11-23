#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x302f00..0x302f4c: record a radio request in the state block at
 * (uintptr_t)&em9305_ram_8015c4 (+28 owner, +24 handle), submit the record {2, -, a, b, 0, 0}
 * through 30fc28, then either run the follow-up (busy flag at +0 set and
 * no override) or the no-op hook and a fresh request. */
extern uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t record);
extern uint32_t opencfw_em9305_radio_followup_30fb3c(uint32_t owner, uint32_t handle);
extern void opencfw_em9305_dispatch_noop_30fd30(void);
extern uint32_t opencfw_em9305_radio_request_30faec(uintptr_t owner, uint32_t handle);

struct opencfw_em9305_radio_record {
    uint8_t kind;
    uint32_t first;
    uint32_t second;
    uint32_t third;
    uint32_t fourth;
};

uint32_t opencfw_em9305_dispatch_child_302f00(uintptr_t owner, uint32_t handle,
                                              uint32_t first, uint32_t second,
                                              uint32_t override)
{
    struct opencfw_em9305_radio_record record;
    em9305_ram_8015dc.u32_8015e0=(uint32_t)owner;
    record.fourth=0u;
    record.third=0u;
    record.second=second;
    record.first=first;
    record.kind=2u;
    em9305_ram_8015dc.u16_8015dc=(uint16_t)handle;
    (void)opencfw_em9305_radio_record_30fc28((uintptr_t)&record);
    if(em9305_ram_8015c4.u8_8015c4!=0u&&override==0u)
        return opencfw_em9305_radio_followup_30fb3c((uint32_t)owner,handle);
    opencfw_em9305_dispatch_noop_30fd30();
    return opencfw_em9305_radio_request_30faec(owner,handle);
}
