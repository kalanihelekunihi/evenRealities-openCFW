#include <stdint.h>

/* Native 0x32ae70..0x32b04a: connection-parameter / PHY update procedure
 * hook on an LL control opcode. The opcode (and, for an unknown/reject
 * response 0x0c, the rejected opcode at 0x802818 and error at 0x80281c)
 * selects an event 0..7; unrelated opcodes return 0. Idle (+620 = 0):
 * run the 4x8 action/transition tables at 0x3354c4/0x335544 on the
 * state byte +623 and enter the procedure (timer code 17 at +635) on a
 * non-zero next state. Running (+620 = 1): a pending expected opcode
 * (+635 = 2..4, 7 or 0x15) is recorded in +644 for events 1/4; on the
 * awaited response (0x11) step the tables and complete (32c818/32c810)
 * when they reach state 0; otherwise reject (32698c), request again
 * (32ca74, bit 17) or report the rejection (322fdc). Returns 1 when the
 * opcode belonged to the procedure. */
extern const uintptr_t opencfw_em9305_slave_conn_upd_actions_3354c4[32];
extern const uint8_t opencfw_em9305_slave_conn_upd_transitions_335544[32];
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t record);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t record);
extern uint32_t opencfw_em9305_child_32ca74(uintptr_t record);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t record, uint32_t reason, uint32_t local);
extern uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t record, uint32_t status);

static uint32_t opencfw_em9305_upd_step_32ae70(uintptr_t record, uint32_t event)
{
    volatile uint8_t *state=(volatile uint8_t *)(record+623u);
    uintptr_t action=opencfw_em9305_slave_conn_upd_actions_3354c4[*state*8u+event];
    if(action!=0u)((void (*)(uintptr_t,uintptr_t))action)(record,action);
    return opencfw_em9305_slave_conn_upd_transitions_335544[*state*8u+event];
}

uint32_t opencfw_em9305_callback_32ae70(uintptr_t record, int32_t opcode)
{
    volatile uint8_t *r=(volatile uint8_t *)record;
    volatile uint32_t *pending=(volatile uint32_t *)(record+644u);
    uint32_t event;
    if(opcode>=30){
        if(opcode==30){
            event=3u;
        }else if(opcode==0x6e){
            if(r[635]!=0x11u)return 0u;
            event=6u;
        }else if(opcode==0x70){
            if(((*pending^(1u<<17))|*(volatile uint32_t *)(record+648u))!=0u)return 0u;
            *(volatile uint32_t *)(record+648u)=0u;
            *pending=0u;
            event=7u;
        }else{
            return 0u;
        }
    }else if(opcode==12){
        int32_t rejected=*(volatile uint8_t *)(uintptr_t)0x802818u;
        if(rejected<13){
            if(rejected==0){
                event=4u;
            }else{
                if(rejected!=7)return 0u;
                if(*(volatile uint8_t *)(uintptr_t)0x80281cu!=15u)return 0u;
                *(volatile uint32_t *)(record+544u)&=~2u;
                event=5u;
            }
        }else if(rejected==13){
            if(r[635]!=0x11u)return 0u;
            event=5u;
        }else if(rejected==17){
            if((uint32_t)(*(volatile uint8_t *)(uintptr_t)0x80281cu-15u)>=2u)return 0u;
            event=5u;
        }else if(rejected==15){
            event=1u;
        }else{
            return 0u;
        }
    }else if(opcode==0x15){
        event=0u;
    }else if(opcode==0x1d){
        event=2u;
    }else{
        return 0u;
    }
    uint32_t current=r[620];
    if(current==0u){
        uint32_t next=opencfw_em9305_upd_step_32ae70(record,event);
        r[623]=(uint8_t)next;
        if(next!=0u){
            r[620]=1u;
            r[635]=17u;
            r[628]=0u;
        }
        return 1u;
    }
    if(current!=1u)return 1u;
    uint32_t awaited;
    if(event==1u||event==4u){
        uint32_t expected=r[635];
        if(expected-2u<3u||expected==7u){
            uint32_t word=*pending;
            r[635]=17u;
            r[631]=1u;
            *pending=word|(1u<<expected);
            awaited=0x11u;
        }else if(expected==0x15u){
            uint32_t word=*pending;
            r[635]=17u;
            *pending=word|(1u<<21);
            awaited=0x11u;
        }else{
            awaited=expected;
        }
    }else{
        awaited=r[635];
    }
    if(awaited==0x11u){
        uint32_t next=opencfw_em9305_upd_step_32ae70(record,event);
        r[623]=(uint8_t)next;
        if(next!=0u)return 1u;
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
    }else if(event==1u){
        (void)opencfw_em9305_phy_reject_32698c(record,0x2au,1u);
    }else if(event==5u){
        uint32_t word=*pending;
        uint32_t state=r[623];
        *(volatile uint32_t *)(record+648u)=0u;
        *pending=word&~(1u<<17);
        if(state!=0u)r[623]=0u;
        (void)opencfw_em9305_mode_event_322fdc(record,*(volatile uint8_t *)(uintptr_t)0x80281du);
    }else if(event==4u){
        (void)opencfw_em9305_phy_reject_32698c(record,0x2au,0u);
    }
    return 1u;
}
