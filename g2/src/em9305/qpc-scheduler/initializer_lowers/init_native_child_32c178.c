#include <stdint.h>

/* Native 0x32c178..0x32c1d4: per-state completion check on the context
 * at +44. State 5: decode the received header into 0x8019fc and, for an
 * LL control opcode 0x22 on LLID 5 with the auxiliary hook (0x802954)
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
        (void)opencfw_em9305_child_32db0c(0x8019fcu,pdu);
        if(*(volatile uint8_t *)(uintptr_t)0x801a00u!=0x22u)return 0u;
        if(*(volatile uint8_t *)(uintptr_t)0x8019fcu!=5u)return 0u;
        if(*(volatile uint32_t *)(uintptr_t)0x802954u==0u)return 0u;
        *(volatile uint8_t *)(link+2252u)=0u;
        *(volatile uint8_t *)(link+2260u)=1u;
        (void)opencfw_em9305_auxiliary_signal_304394();
        return 0u;
    }
    if(state==3u&&*(volatile uint8_t *)(context+152u)!=0u)
        return opencfw_em9305_child_3257e4(record,*(volatile uint8_t *)(context+149u));
    return 0u;
}
