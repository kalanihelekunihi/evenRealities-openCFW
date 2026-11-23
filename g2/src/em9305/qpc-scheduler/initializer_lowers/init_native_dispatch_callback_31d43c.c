#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31d43c..0x31d5e8: periodic-advertising-with-responses receive
 * completion for the owner's advertising set (+36). The response header
 * is decoded (317a98). Status 0 counts the event ((uintptr_t)&em9305_ram_8029ac +5 and the
 * per-subevent counter at +120) and resets +246. Only a role-2 set with
 * status 0, 3, 4 or 5 continues (6 reports event 6): the first such
 * event latches the response timing (+252), status 3 reschedules the
 * next anchor (317ebc/302f4c) and sets the done flag, status 0 records
 * the response filter and parks the buffer in a free slot, statuses 0/4
 * refresh the subevent's RSSI (+100; 4 also counts +76). Then the train
 * is advanced (31d150 or 31d2bc per +31) and the report produced
 * (31d5e8); failures signal the auxiliary hook. Status 0 keeps a new
 * response buffer at ((uintptr_t)&em9305_ram_8029ac + 0x14u) (filter +274); any other buffer is
 * released. */
extern uint32_t opencfw_em9305_dispatch_child_317a98(uintptr_t out, uintptr_t in);
extern uint32_t opencfw_em9305_dispatch_event_send_31d128(uintptr_t set, uint32_t event);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_302f4c(uint32_t start, uint32_t window, uintptr_t channel);
extern uint32_t opencfw_em9305_dispatch_child_31d150(uintptr_t set, uintptr_t done);
extern uint32_t opencfw_em9305_dispatch_child_31d2bc(uintptr_t set, uintptr_t done);
extern uint32_t opencfw_em9305_dispatch_child_31d5e8(uintptr_t set, uint32_t done, uintptr_t buffer);
extern uint32_t opencfw_em9305_auxiliary_signal_304394(void);
extern uint32_t opencfw_em9305_ll_receive_buffer_release_31761c(uintptr_t buffer);

void opencfw_em9305_dispatch_callback_31d43c(uintptr_t owner, uintptr_t buffer, uint32_t status)
{
    const uintptr_t state=(uintptr_t)&em9305_ram_8029ac;
    volatile uint8_t *s8=(volatile uint8_t *)state;
    volatile uint32_t *s32=(volatile uint32_t *)state;
    uint8_t header[8] __attribute__((aligned(4)));
    uintptr_t set=*(volatile uint32_t *)(owner+36u);
    volatile uint8_t *a=(volatile uint8_t *)set;
    header[7]=0u;
    (void)opencfw_em9305_dispatch_child_317a98((uintptr_t)header,buffer);
    if(status==0u){
        uint32_t index=s8[0];
        uint32_t events=s8[5];
        volatile uint8_t *counter=(volatile uint8_t *)(state+index+120u);
        uint32_t count=*counter;
        s8[5]=(uint8_t)(events+1u);
        *counter=(uint8_t)(count+1u);
        *(volatile uint16_t *)(set+246u)=0u;
    }
    uint32_t ok=0u;
    if(a[1]!=2u||status-1u<2u)goto finish;
    if(status==6u){
        (void)opencfw_em9305_dispatch_event_send_31d128(set,6u);
        goto finish;
    }
    if(s8[6]==0u){
        s8[6]=1u;
        if((status|4u)==4u)
            *(volatile uint32_t *)(set+252u)=*(volatile uint32_t *)(set+188u)-
                                             *(volatile uint32_t *)(set+264u);
    }
    if(status==3u){
        uint32_t latched=*(volatile uint32_t *)(set+252u);
        uint32_t anchor=*(volatile uint32_t *)(set+264u);
        uint32_t time=s32[3];
        uint32_t reference=*(volatile uint32_t *)(set+248u);
        uint32_t skew=*(volatile uint16_t *)(set+246u);
        uint32_t window=*(volatile uint16_t *)(set+244u);
        uint32_t start=time+anchor+latched;
        uint32_t widening=opencfw_em9305_init_secondary_time_317ebc(start-reference+skew,window);
        uint32_t span=*(volatile uint16_t *)(set+246u)+(widening<<1);
        uintptr_t channel=s32[4];
        *(volatile uint32_t *)(set+172u)=span;
        (void)opencfw_em9305_dispatch_child_302f4c(start-widening,span,channel);
        header[7]=1u;
    }else if(status==0u||status==4u){
        if(status==0u){
            uint32_t kind=header[0];
            uint32_t filter=header[2];
            uint32_t subevent=header[1];
            s8[7]=(uint8_t)filter;
            s8[8]=(uint8_t)subevent;
            if(kind!=3u&&(kind!=1u||header[3]!=0u)){
                volatile uint32_t *entry=(volatile uint32_t *)(state+24u+s8[0]*24u+s8[1]*4u);
                if(*entry==0u&&s8[3]==0u){
                    *entry=(uint32_t)buffer;
                    buffer=0u;
                }
            }
        }
        *(volatile uint32_t *)(set+248u)=*(volatile uint32_t *)(set+188u);
    }
    {
        uint32_t index=s8[0];
        if(index<a[52]){
            if(status==4u){
                volatile uint32_t *slot=(volatile uint32_t *)(set+56u+index*4u);
                *(volatile uint8_t *)(*slot+100u)=a[192];
                *(volatile uint32_t *)(*slot+76u)+=1u;
            }else if(status==0u){
                *(volatile uint8_t *)(*(volatile uint32_t *)(set+56u+index*4u)+100u)=a[192];
            }
        }
    }
    if(a[31]==1u)ok=opencfw_em9305_dispatch_child_31d150(set,(uintptr_t)&header[7]);
    else ok=opencfw_em9305_dispatch_child_31d2bc(set,(uintptr_t)&header[7]);
    if(ok!=0u){
        ok=1u;
        goto report;
    }
finish:
    (void)opencfw_em9305_auxiliary_signal_304394();
    ok=0u;
report:
    {
        uintptr_t keep=buffer;
        if(ok!=0u){
            if(status==0u&&header[0]==3u){
                (void)opencfw_em9305_auxiliary_signal_304394();
            }else if(opencfw_em9305_dispatch_child_31d5e8(set,header[7],buffer)!=0u){
                keep=0u;
            }else{
                (void)opencfw_em9305_auxiliary_signal_304394();
            }
        }
        if(status==0u&&header[0]==3u&&s32[5]==0u&&header[1]!=a[274]){
            s32[5]=(uint32_t)keep;
            a[274]=header[1];
            return;
        }
        if(keep!=0u)(void)opencfw_em9305_ll_receive_buffer_release_31761c(keep);
    }
}
