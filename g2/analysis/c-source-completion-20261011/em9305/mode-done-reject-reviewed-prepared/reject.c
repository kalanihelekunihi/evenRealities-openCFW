#include <stdint.h>

/* Complete native 0x3233b4..0x323422, including global mode7 special
 * side effects before the distinct reject event children. */
extern uint32_t opencfw_em9305_mode_event_323314(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_mode_event_3232a8(uintptr_t,uint32_t);
uint32_t opencfw_em9305_mode_reject_3233b4(uintptr_t context,
                                             uint32_t selector)
{
    uint32_t flags=*(volatile uint32_t *)(context+636u);
    uint32_t mask=1u<<(selector&31u);
    if((flags&mask)==0u) return (uint32_t)context;
    uint32_t global=*(volatile uint8_t *)(uintptr_t)0x802818u;
    uint32_t reason=26u;
    flags&=~mask;
    *(volatile uint32_t *)(context+640u)=0u;
    *(volatile uint32_t *)(context+636u)=flags;
    if(global==7u) {
        if(selector==4u) {
            uint32_t word=*(volatile uint32_t *)(context+544u);
            *(volatile uint32_t *)(context+544u)=word&~(1u<<5u);
            return (uint32_t)context;
        }
        if(selector==7u) {
            uint32_t word=*(volatile uint32_t *)(context+544u);
            *(volatile uint32_t *)(context+544u)=word&~(1u<<26u);
            return opencfw_em9305_mode_event_3232a8(context,17u);
        }
    } else if(global==17u || global==13u) {
        reason=*(volatile uint8_t *)(uintptr_t)0x80281du;
    }
    if(selector==2u) return opencfw_em9305_mode_event_323314(context,reason);
    if(selector==7u) return opencfw_em9305_mode_event_3232a8(context,reason);
    return (uint32_t)context;
}
