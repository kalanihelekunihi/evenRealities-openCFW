#include <stdint.h>

/* Native 0x32b210..0x32b2d0: dispatch an LL control opcode for a link.
 * Opcode 0x1c with a pending mode report (+526) reports it (323374).
 * Otherwise the twelve optional procedure handlers at 0x80569c are
 * offered the PDU in order; the first non-zero answer is returned, and
 * if none claims it the default handler 31c420 runs. */
extern uint32_t opencfw_em9305_mode_event_323374(uintptr_t record);
extern uint32_t opencfw_em9305_mode_event_31c420(uintptr_t record, uint32_t opcode);

uint32_t opencfw_em9305_child_32b210(uintptr_t record, uint32_t opcode)
{
    if(opcode==0x1cu&&*(volatile uint8_t *)(record+526u)!=0u)
        return opencfw_em9305_mode_event_323374(record);
    volatile const uint32_t *handlers=(volatile const uint32_t *)(uintptr_t)0x80569cu;
    for(uint32_t index=0u;index<12u;++index){
        uintptr_t handler=handlers[index];
        if(handler==0u)continue;
        uint32_t result=((uint32_t (*)(uintptr_t,uint32_t,uintptr_t))handler)(record,opcode,handler);
        if(result!=0u)return result;
    }
    return opencfw_em9305_mode_event_31c420(record,opcode);
}
