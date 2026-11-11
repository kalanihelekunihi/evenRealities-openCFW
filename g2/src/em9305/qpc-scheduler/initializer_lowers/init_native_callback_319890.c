#include <stdint.h>

/* Native 0x319890..0x319950: PHY-update procedure hook for LL control
 * opcodes, active only while bit 4 of 0x805a94 is set (else returns 0).
 * Opcode 0x70 consumes the deferred bit 20 of +644 (mode 0), 0x53/0x54
 * select modes 3/4, and an unknown-response (0x0c) for the rejected
 * opcode at 0x802818 (0x13, 0x12, or 7 rejecting 0x12) selects 2 or 1.
 * Idle (+620 = 0): start through 324d6c and, unless +622 is set, enter
 * state 1 with timer code 20 at +635. Running: on code 20 finish through
 * 324d6c and 32c810 unless +622 is set; otherwise defer by setting bit
 * 20 of +644. Returns 1 when a mode was selected. */
extern uint32_t opencfw_em9305_child_324d6c(uintptr_t record, uint32_t mode);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t record);

uint32_t opencfw_em9305_callback_319890(uintptr_t record, uint32_t opcode)
{
    uint32_t mode;
    if((*(volatile uint8_t *)(uintptr_t)0x805a94u&0x10u)==0u)return 0u;
    volatile uint32_t *deferred=(volatile uint32_t *)(record+644u);
    if(opcode==0x70u){
        uint32_t word=*deferred;
        if((word&(1u<<20))==0u)return 0u;
        *(volatile uint32_t *)(record+648u)=0u;
        *deferred=word&~(1u<<20);
        mode=0u;
    }else if(opcode==0x53u){
        mode=3u;
    }else if(opcode==0x54u){
        mode=4u;
    }else if(opcode==0x0cu){
        uint32_t rejected=*(volatile uint8_t *)(uintptr_t)0x802818u;
        if(rejected==0x13u)mode=2u;
        else if(rejected==0x12u)mode=1u;
        else if(rejected==7u&&*(volatile uint8_t *)(uintptr_t)0x80281cu==0x12u)mode=2u;
        else return 0u;
    }else{
        return 0u;
    }
    volatile uint8_t *state=(volatile uint8_t *)(record+620u);
    volatile uint8_t *code=(volatile uint8_t *)(record+635u);
    uint32_t current=*state;
    if(current==0u){
        (void)opencfw_em9305_child_324d6c(record,mode);
        if(*(volatile uint8_t *)(record+622u)!=0u){
            *state=1u;
            *code=20u;
        }
    }else if(current==1u){
        if(*code!=20u){
            *deferred|=1u<<20;
        }else{
            (void)opencfw_em9305_child_324d6c(record,mode);
            if(*(volatile uint8_t *)(record+622u)==0u){
                *state=0u;
                *code=0xffu;
                (void)opencfw_em9305_phy_finish_32c810(record);
            }
        }
    }
    return 1u;
}
