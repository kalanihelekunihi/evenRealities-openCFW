#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32c178..0x32c1d4: per-state completion check on the context
 * at +44. State 5: decode the received header into ((uintptr_t)&em9305_ram_8019e8 + 0x14u) and, for an
 * LL control opcode 0x22 on LLID 5 with the auxiliary hook (((uintptr_t)&em9305_ram_802950 + 0x4u))
 * armed, clear +2252 / set +2260 of the link (+36) and signal it. State 3
 * with +152 set: return 3257e4(record, +149). Otherwise returns 0. */
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t out, uintptr_t in);
extern uint32_t opencfw_em9305_child_3257e4(uintptr_t record, uint32_t value);
extern uint32_t opencfw_em9305_auxiliary_signal_304394(void);

uint32_t opencfw_em9305_child_32c178(uintptr_t record, uintptr_t pdu)
{
    uintptr_t context=*(volatile uint32_t *)(record+44u);
    uint32_t state=*(volatile uint8_t *)(context+148u);
    if(state==5u){
        uintptr_t link=*(volatile uint32_t *)(record+36u);
        (void)opencfw_em9305_child_32db0c(((uintptr_t)&em9305_ram_8019e8 + 0x14u),pdu);
        if(em9305_ram_8019e8.u8_801a00!=0x22u)return 0u;
        if(em9305_ram_8019e8.u8_8019fc!=5u)return 0u;
        if(em9305_ram_802950.u32_802954==0u)return 0u;
        *(volatile uint8_t *)(link+2252u)=0u;
        *(volatile uint8_t *)(link+2260u)=1u;
        (void)opencfw_em9305_auxiliary_signal_304394();
        return 0u;
    }
    if(state==3u&&*(volatile uint8_t *)(context+152u)!=0u)
        return opencfw_em9305_child_3257e4(record,*(volatile uint8_t *)(context+149u));
    return 0u;
}
