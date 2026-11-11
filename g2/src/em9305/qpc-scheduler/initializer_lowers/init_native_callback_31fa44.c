#include <stdint.h>

/* Native 0x31fa44..0x31fb98: LL control hook for the data-length/PHY
 * procedure on a connection. While a request is outstanding (+403),
 * opcodes 13/14 and unknown/reject responses for opcodes outside the
 * 0x228f4 set finish it through 31b714. An LL 0x18 (or a pending
 * response, +620) may start 31af38. With the feature bit 0 of 0x805a94
 * the opcode selects a mode (0x70 consumes deferred bit 19 of +644,
 * 0x18 -> 0, 0x3e -> 5, and an unknown response 0x0c maps the rejected
 * opcode at 0x802818 to 1..6), which then starts (+620 = 0) or finishes
 * (+620 = 1, timer code 0x13 at +635) the procedure through 31fa10;
 * otherwise the request is deferred in bit 19. Returns 1 when the
 * procedure was driven. */
extern uint32_t opencfw_em9305_child_31b714(uintptr_t record);
extern uint32_t opencfw_em9305_child_31af38(uintptr_t record);
extern uint32_t opencfw_em9305_child_31fa10(uintptr_t record, uint32_t mode);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t record);

static uint32_t opencfw_em9305_reject_mode_31fa44(uintptr_t record, uint32_t *mode)
{
    uint32_t rejected=*(volatile uint8_t *)(uintptr_t)0x802818u;
    switch(rejected){
    case 4u: *mode=1u; return 1u;
    case 5u: *mode=2u; return 1u;
    case 6u: *mode=3u; return 1u;
    case 11u: *mode=4u; return 1u;
    case 7u: case 17u:
        *mode=6u;
        return *(volatile uint8_t *)(uintptr_t)0x80281cu==3u;
    case 13u:
        *mode=6u;
        return *(volatile uint8_t *)(record+635u)==0x13u;
    default:
        return 0u;
    }
}

uint32_t opencfw_em9305_callback_31fa44(uintptr_t record, uint32_t opcode)
{
    volatile uint8_t *state=(volatile uint8_t *)(record+620u);
    volatile uint8_t *code=(volatile uint8_t *)(record+635u);
    volatile uint32_t *deferred=(volatile uint32_t *)(record+644u);
    uint32_t mode;
    if(*(volatile uint8_t *)(record+403u)!=0u){
        if(opcode-13u<2u){
            (void)opencfw_em9305_child_31b714(record);
            return 1u;
        }
        if(opcode==12u){
            uint32_t rejected=*(volatile uint8_t *)(uintptr_t)0x802818u;
            if(rejected>=0x12u||((0x228f4u>>rejected)&1u)==0u){
                (void)opencfw_em9305_child_31b714(record);
                return 0u;
            }
        }
    }
    uint32_t current=*state;
    if(opcode==0x18u&&(current==0u||(current==1u&&*code!=0x13u)))
        (void)opencfw_em9305_child_31af38(record);
    if((*(volatile uint8_t *)(uintptr_t)0x805a94u&1u)==0u)return 0u;
    if(opcode==0x70u){
        uint32_t word=*deferred;
        if((word&(1u<<19))==0u)return 0u;
        *(volatile uint32_t *)(record+648u)=0u;
        *deferred=word&~(1u<<19);
        mode=0u;
    }else if(opcode==0x18u){
        mode=0u;
    }else if(opcode==0x3eu){
        mode=5u;
        if(*code!=0x13u)return 0u;
    }else if(opcode==0x0cu){
        if(opencfw_em9305_reject_mode_31fa44(record,&mode)==0u)return 0u;
    }else{
        return 0u;
    }
    current=*state;
    if(current==1u){
        if(*code!=0x13u){
            *deferred|=1u<<19;
            return 1u;
        }
        (void)opencfw_em9305_child_31fa10(record,mode);
        uint32_t result=*(volatile uint8_t *)(record+621u);
        if(result==5u||result==0u){
            *state=0u;
            *code=0xffu;
            (void)opencfw_em9305_phy_finish_32c810(record);
        }
    }else if(current==0u){
        (void)opencfw_em9305_child_31fa10(record,mode);
        uint32_t result=*(volatile uint8_t *)(record+621u);
        if(result!=0u&&result!=5u){
            *state=1u;
            *code=19u;
        }
    }
    return 1u;
}
