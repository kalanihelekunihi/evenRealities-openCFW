#include <stdint.h>

/* Complete native 0x3234ec..0x323526. The bit-clear and context+640 store
 * precede each child call, including their delay-slot ordering. */
extern uint32_t opencfw_em9305_mode_event_323314(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_mode_event_3232a8(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_mode_event_323374(uintptr_t);
uint32_t opencfw_em9305_mode_done_3234ec(uintptr_t context,
                                           uint32_t selector)
{
    uint32_t flags=*(volatile uint32_t *)(context+636u);
    uint32_t bit=selector&31u;
    if(((flags>>bit)&1u)==0u)
        return (uint32_t)context;
    flags&=~(1u<<bit);
    *(volatile uint32_t *)(context+640u)=0u;
    *(volatile uint32_t *)(context+636u)=flags;
    if(selector==7u) return opencfw_em9305_mode_event_3232a8(context,0u);
    if(selector==3u) return opencfw_em9305_mode_event_323374(context);
    if(selector==2u) return opencfw_em9305_mode_event_323314(context,0u);
    return (uint32_t)context;
}
