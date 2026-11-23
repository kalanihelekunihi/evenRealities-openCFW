#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x320f78..0x321150: master-side connection update / PHY
 * procedure hook on an LL control opcode (the master counterpart of
 * 32ae70, with an 11-event 4-state table at 0x335038/0x3350e8). Unknown
 * response 0x0c maps the rejected opcode at ((uintptr_t)&em9305_ram_8027e0 + 0x38u) (and error at
 * ((uintptr_t)&em9305_ram_8027e0 + 0x3cu)) to events 3, 4 or 7; deferred requests in +644 bits 17/18
 * give events 8/9 on opcode 0x70. Idle (+620 = 0): step the tables and
 * enter the procedure (timer code 17 at +635). Running: for a rejected
 * request record the pending opcode bit, step the tables on the awaited
 * response (completing through 32c818/32c810 at state 0), or re-request
 * (32ca74 bit 17, 32c980 bit 18) or reject (32698c). Returns 1 when the
 * opcode belonged to the procedure. */
typedef void (*opencfw_em9305_mst_conn_action)(void);
extern const opencfw_em9305_mst_conn_action opencfw_em9305_mst_conn_actions_335038[44];
extern const unsigned char opencfw_em9305_mst_conn_transitions_3350e8[44];
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t record);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t record);
extern uint32_t opencfw_em9305_child_32ca74(uintptr_t record);
extern uint32_t opencfw_em9305_child_32c980(uintptr_t record);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t record, uint32_t reason, uint32_t local);

static uint32_t opencfw_em9305_mst_step_320f78(uintptr_t record, uint32_t event)
{
    volatile uint8_t *state=(volatile uint8_t *)(record+623u);
    uintptr_t action=(uintptr_t)opencfw_em9305_mst_conn_actions_335038[*state*11u+event];
    if(action!=0u)((void (*)(uintptr_t,uintptr_t))action)(record,action);
    uint32_t next=opencfw_em9305_mst_conn_transitions_3350e8[*state*11u+event];
    *state=(uint8_t)next;
    return next;
}

uint32_t opencfw_em9305_callback_320f78(uintptr_t record, int32_t opcode)
{
    volatile uint8_t *r=(volatile uint8_t *)record;
    volatile uint32_t *pending=(volatile uint32_t *)(record+644u);
    uint32_t event,rejected_request=0u;
    if(opcode>0x6d){
        if(opcode==0x6e||opcode==0x71){
            if(r[635]!=0x11u)return 0u;
            event=opcode==0x6e?6u:7u;
        }else if(opcode==0x70){
            uint32_t word=*pending,extra=*(volatile uint32_t *)(record+648u);
            if(((word^(1u<<18))|extra)==0u)event=9u;
            else if(((word^(1u<<17))|extra)==0u)event=8u;
            else return 0u;
            *(volatile uint32_t *)(record+648u)=0u;
            *pending=0u;
        }else if(opcode==0x72){
            event=10u;
        }else{
            return 0u;
        }
    }else if(opcode==12){
        uint32_t rejected=em9305_ram_8027e0.u8_802818;
        if(rejected==7u){
            if(em9305_ram_8027e0.u8_80281c!=15u)return 0u;
            *(volatile uint32_t *)(record+544u)&=~2u;
            event=7u;
        }else if(rejected==13u){
            if(r[635]!=0x11u)return 0u;
            event=7u;
        }else if(rejected==15u){
            event=3u;
            rejected_request=1u;
        }else if(rejected==16u){
            event=4u;
        }else if(rejected==17u){
            if(em9305_ram_8027e0.u8_80281c!=15u)return 0u;
            event=7u;
        }else{
            return 0u;
        }
    }else if(opcode==0x15){
        event=0u;
    }else if(opcode==0x1d){
        event=1u;
    }else if(opcode==0x1e){
        event=2u;
    }else{
        return 0u;
    }
    uint32_t current=r[620];
    if(current==0u){
        if(opencfw_em9305_mst_step_320f78(record,event)!=0u){
            r[620]=1u;
            r[635]=17u;
            r[628]=0u;
        }
        return 1u;
    }
    if(current!=1u)return 1u;
    uint32_t expected=r[635];
    uint32_t awaited=expected==0x11u;
    if(rejected_request!=0u&&(expected-2u<3u||expected==7u)){
        uint32_t word=*pending;
        r[635]=17u;
        r[631]=1u;
        *pending=word|(1u<<expected);
        awaited=1u;
    }
    if(awaited!=0u){
        if(opencfw_em9305_mst_step_320f78(record,event)!=0u)return 1u;
        (void)opencfw_em9305_phy_complete_32c818(record);
        uint32_t flags=r[13];
        r[620]=0u;
        r[635]=0xffu;
        r[13]=(uint8_t)(flags&~1u);
        (void)opencfw_em9305_phy_finish_32c810(record);
        return 1u;
    }
    if(event==0u){
        (void)opencfw_em9305_child_32ca74(record);
        *pending|=1u<<17;
    }else if(event==3u){
        if(expected!=0x13u){
            (void)opencfw_em9305_phy_reject_32698c(record,0x2au,1u);
        }else{
            (void)opencfw_em9305_child_32c980(record);
            *pending|=1u<<18;
        }
    }
    return 1u;
}
