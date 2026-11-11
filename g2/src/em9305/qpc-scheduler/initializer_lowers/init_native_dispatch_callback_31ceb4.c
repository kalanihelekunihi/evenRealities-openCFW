#include <stdint.h>

/* Native 0x31ceb4..0x31d0fc: BIG/CIG receive event completion for the
 * group (object +36). Received PDUs left in the per-stream buffer table
 * (0x8029ac + 24 + 24 i + 4 j, streams +52, subevents +24) are handed to
 * live streams (317524, slot cleared) or released. Outside state 2 the
 * group reports status 7 (31d128), stops its timer (+208) and drops the
 * control PDU (0x8029ac +20). In state 2 a received control PDU is first
 * checked by the MIC hook (*0x8051dc, with the 64-bit event counter
 * +32/+36 times +24 published through +464) when encryption is on (+484);
 * a rejected PDU is released with status 6 and ends the event. Otherwise
 * an unhandled channel-map (0) or terminate (1) BIG control PDU is parsed
 * (317a44 / 317a84) and its instant (+276 / +288) recorded in the pending
 * mask +272 unless already past (a past terminate reports status 4 and
 * state 30 at +290), the PDU is released, and the timeout timer restarted
 * when 0x8029b1 is set. Then the group advances event by event (counter
 * +32/+36, anchor +252, object timing +8/+20, offset +172), applying a
 * due channel map (32520c) and reporting a pending terminate, until the
 * schedule insert succeeds; finally 31d6a4 runs and, when enabled
 * (0x805aaf), the event counter is reported (32324c). */
extern uint32_t opencfw_em9305_dispatch_child_317524(uint32_t a,uint32_t b,uint32_t c);
extern uint32_t opencfw_em9305_ll_receive_buffer_release_31761c(uintptr_t buffer);
extern uint32_t opencfw_em9305_dispatch_event_send_31d128(uintptr_t record,
                                                          uint32_t status);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer,
                                                  uint32_t milliseconds);
extern uint32_t opencfw_em9305_dispatch_child_317a44(uintptr_t value_out,
    uintptr_t half_out,uintptr_t in);
extern uint32_t opencfw_em9305_dispatch_child_317a84(uint32_t a,uint32_t b,uint32_t c);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t first,
                                                          uint32_t second);
extern uint32_t opencfw_em9305_dispatch_child_3257f4(uintptr_t context);
extern uint32_t opencfw_em9305_dispatch_child_32520c(uintptr_t object,
    uint32_t first,uint32_t second);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,
                                                                 uintptr_t tie);
extern uint32_t opencfw_em9305_dispatch_child_31d6a4(uintptr_t group,
    uint32_t counter,uint32_t anchor);
extern uint32_t opencfw_em9305_dispatch_child_32324c(uint32_t handle,uint32_t value);
typedef uint32_t (*opencfw_em9305_mic_hook_t)(uintptr_t context,uintptr_t packet);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

#define RX 0x8029acu

void opencfw_em9305_dispatch_callback_31ceb4(uintptr_t object)
{
    uintptr_t group=r32(object+36u);
    uint32_t first_counter=r32(group+32u);
    uint32_t anchor=r32(group+40u)+r32(group+252u);
    uint32_t done=0u;
    for(uint32_t stream=0u;stream<r8(group+52u);++stream){
        uintptr_t slot=RX+24u+stream*24u;
        for(uint32_t sub=0u;sub<r8(group+24u);++sub,slot+=4u){
            uintptr_t buffer=r32(slot);
            if(buffer==0u)continue;
            uintptr_t target=r32(group+stream*4u+56u);
            if(target!=0u){
                (void)opencfw_em9305_dispatch_child_317524(target,buffer,(uint8_t)sub);
                w32(slot,0u);
            }else{
                (void)opencfw_em9305_ll_receive_buffer_release_31761c(buffer);
            }
        }
    }
    if(r8(group+1u)!=2u){
        (void)opencfw_em9305_dispatch_event_send_31d128(group,7u);
        (void)opencfw_em9305_wsf_timer_stop(group+208u);
        uintptr_t control=r32(RX+20u);
        if(control!=0u){
            (void)opencfw_em9305_ll_receive_buffer_release_31761c(control);
            w32(RX+20u,0u);
        }
        return;
    }
    uintptr_t control=r32(RX+20u);
    uintptr_t pending=group+272u;
    if(control!=0u){
        uint32_t rejected=0u;
        if(r8(group+484u)!=0u){
            uintptr_t hook=r32(0x8051dcu);
            if(hook!=0u){
                uint32_t burst=r8(group+24u);
                uint64_t counter=((uint64_t)r32(group+36u)<<32|r32(group+32u))*burst;
                uint32_t value[2];
                w32(group+464u,(uint32_t)(uintptr_t)value);
                value[0]=(uint32_t)counter;
                value[1]=(uint32_t)(counter>>32);
                uint32_t accepted=((opencfw_em9305_mic_hook_t)hook)(group+428u,control);
                control=r32(RX+20u);
                if(accepted==0u){
                    (void)opencfw_em9305_ll_receive_buffer_release_31761c(control);
                    w32(RX+20u,0u);
                    (void)opencfw_em9305_dispatch_event_send_31d128(group,6u);
                    done=1u;
                    rejected=1u;
                }
            }
        }
        if(!rejected){
            if(r8(pending)==0u){
                uint32_t opcode=r8(control+2u);
                if(opcode==0u){
                    (void)opencfw_em9305_dispatch_child_317a44(group+280u,group+276u,
                                                               control+2u);
                    if((int16_t)(r16(group+276u)-r16(group+32u))>=0)
                        w8(pending,r8(pending)|1u);
                }else if(opcode==1u){
                    (void)opencfw_em9305_dispatch_child_317a84(group+290u,group+288u,
                                                               control+2u);
                    if((int16_t)(r16(group+288u)-r16(group+32u))<0){
                        w8(group+290u,30u);
                        (void)opencfw_em9305_dispatch_event_send_31d128(group,4u);
                    }else{
                        w8(pending,r8(pending)|2u);
                    }
                }
            }
            (void)opencfw_em9305_ll_receive_buffer_release_31761c(r32(RX+20u));
            done=0u;
            w32(RX+20u,0u);
        }
    }
    if(done==0u){
        if(r8(RX+5u)!=0u)
            (void)opencfw_em9305_wsf_timer_start_ms(group+208u,r32(group+224u));
        for(;;){
            uint32_t interval=r32(group+16u);
            uint32_t base=r32(group+252u)+interval;
            uint32_t offset=r32(group+264u);
            uint32_t low=r32(group+32u);
            uint32_t start=r32(group+248u);
            uint32_t high=r32(group+36u);
            uint32_t extra=r16(group+246u);
            uint32_t selector=r16(group+244u);
            uint64_t next=((uint64_t)high<<32|low)+1u;
            w32(group+36u,(uint32_t)(next>>32));
            w32(group+32u,(uint32_t)next);
            w32(group+252u,base);
            uint32_t time=opencfw_em9305_init_secondary_time_317ebc(
                offset+base-start+extra,selector);
            uint32_t period=r32(group+16u);
            uint32_t current=r32(group+252u);
            uint32_t window=r32(group+264u);
            w32(object+20u,period);
            w32(object+8u,current-time+window);
            w32(group+172u,r16(group+246u)+time*2u);
            (void)opencfw_em9305_dispatch_child_3257f4(group);
            uint32_t flags=r8(pending);
            if(flags!=0u){
                if((flags&1u)!=0u
                   &&(uint16_t)(r16(group+32u)+1u)==r16(group+276u)){
                    uint32_t map_high=r32(group+284u),map_low=r32(group+280u);
                    w8(pending,flags&~1u);
                    (void)opencfw_em9305_dispatch_child_32520c(group,map_low,map_high);
                    flags=r8(pending);
                }
                if((flags&2u)!=0u)
                    (void)opencfw_em9305_dispatch_event_send_31d128(group,4u);
            }
            if(opencfw_em9305_associated_schedule_insert_312da4(object,0u)!=0u)break;
        }
    }
    (void)opencfw_em9305_dispatch_child_31d6a4(group,first_counter,anchor);
    if(r8(0x805aafu)!=0u)
        (void)opencfw_em9305_dispatch_child_32324c(r8(group+2u),r32(group+32u));
}
