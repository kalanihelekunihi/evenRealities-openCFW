#include <stdint.h>

/* Native 0x321648..0x3217f0: periodic-advertising sync event callback for
 * the secondary context (object +36). A pending stop (+3) sends message 5
 * and a pending terminate (+2) runs 326108 and stops the sync timer; both
 * return. Otherwise a sync that missed its expected number of events
 * (+248 - +278 == 5, or 6 with +8) sends message 3. A received sync
 * (0x803d71) restarts the timeout timer (+700, +620 ms), records the
 * event counter (+276) and anchor (0x803d74 -> +272) and derives the skip
 * (+616 within the timeout, else timeout*1000 / interval). The elapsed
 * events (+248 - +276) are reported (30e89c) when reporting is enabled
 * (0x805bee). Then, for each skip step, the three subevent streams
 * (+312 + 96 k) receive event 324904, the event counter advances, the
 * object is re-timed (+8/+12/+20, context +204/+264/+268) and a channel
 * is selected, until the schedule insert succeeds. */
extern uint32_t opencfw_em9305_init_secondary_message_325d50(uintptr_t record,
                                                            uint32_t reason);
extern uint32_t opencfw_em9305_child_326108(uintptr_t record,uint32_t value);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer,
                                                  uint32_t milliseconds);
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t selector);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t first,
                                                          uint32_t second);
extern uint32_t opencfw_em9305_associated_report_30e89c(uint32_t,uint32_t,uint32_t,
                                                        uint32_t,uint32_t);
extern void opencfw_em9305_child_324904(uintptr_t event);
extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t channels,
                                                              uint32_t seed);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,
                                                                 uintptr_t tie);
extern uintptr_t opencfw_em9305_init_secondary_compare_3249e8(uintptr_t first,
                                                         uintptr_t second);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

uint32_t opencfw_em9305_callback_321648(uintptr_t object)
{
    uintptr_t context=r32(object+36u);
    if(r8(context+3u)!=0u){
        w8(context+3u,0u);
        return opencfw_em9305_init_secondary_message_325d50(context,5u);
    }
    if(r8(context+2u)!=0u){
        w8(context+2u,0u);
        (void)opencfw_em9305_child_326108(context,3u);
        return opencfw_em9305_wsf_timer_stop(context+700u);
    }
    if(r8(context+5u)==0u){
        uint32_t extra=r8(context+8u)!=0u;
        uint32_t expected=r16(context+278u);
        if(r16(context+248u)-expected==extra+5u)
            (void)opencfw_em9305_init_secondary_message_325d50(context,3u);
    }
    uint32_t skip=1u;
    w8(context+8u,0u);
    if(r8(0x803d71u)!=0u){
        uint32_t counter=r16(context+248u);
        uint32_t anchor=r32(0x803d74u);
        uint32_t timeout=r32(context+620u);
        w16(context+276u,counter);
        w32(context+272u,anchor);
        w8(0x803d71u,0u);
        (void)opencfw_em9305_wsf_timer_start_ms(context+700u,timeout);
        uint32_t interval=r32(context+260u);
        if(interval!=0u){
            uint32_t limit=r32(context+620u)*1000u;
            if(interval<limit){
                skip=r16(context+616u);
            }else{
                uint32_t period=r32(context+252u);
                if(period!=0u)skip=limit/period;
            }
        }
    }
    uint32_t elapsed=r16(context+248u)-r16(context+276u);
    int32_t index=(int32_t)(context-0x803d78u)/784;
    if(r8(0x805beeu)!=0u){
        uint32_t span=r32(context+252u)*(uint16_t)elapsed;
        uint32_t factor=opencfw_em9305_mode_callback_child_317ea4(r8(context+256u));
        uint32_t time=opencfw_em9305_init_secondary_time_317ebc(span,factor);
        (void)opencfw_em9305_associated_report_30e89c((uint8_t)index,
            r16(context+248u),(uint16_t)time,r32(context+252u),r32(object+8u));
    }
    uint32_t handle=(uint8_t)index;
    for(;;){
        _Alignas(4) uint8_t event[8];
        *(uint16_t *)(void *)(event+6)=(uint16_t)handle;
        *(uint16_t *)(void *)(event+2)=(uint16_t)skip;
        *(uint16_t *)(void *)event=(uint16_t)r16(context+248u);
        for(uint32_t stream=0u;stream<3u;++stream){
            if(r8(context+312u+stream*96u)==0u)continue;
            event[4]=(uint8_t)stream;
            opencfw_em9305_child_324904((uintptr_t)event);
        }
        uint32_t counter=r16(context+248u);
        uint32_t period=r32(context+252u);
        uint32_t selector=r8(context+256u);
        elapsed+=skip;
        uint32_t span=period*(uint16_t)elapsed;
        w16(context+248u,counter+skip);
        uint32_t factor=opencfw_em9305_mode_callback_child_317ea4(selector);
        uint32_t time=opencfw_em9305_init_secondary_time_317ebc(span,factor);
        uint32_t current=r32(context+252u);
        uint32_t base=r32(context+264u);
        uint32_t window=r32(context+268u);
        uint32_t scaled=current*(uint16_t)elapsed;
        uint32_t start=r32(context+272u);
        uint32_t seed=r16(context+248u);
        w32(object+8u,scaled-time+start);
        w32(object+12u,base+time);
        w32(context+204u,window+time*2u);
        w32(object+20u,current);
        uint32_t chosen=opencfw_em9305_associated_channel_seed_324c98(context+644u,seed);
        w8(context+97u,chosen);
        uint32_t inserted=opencfw_em9305_associated_schedule_insert_312da4(object,
            (uintptr_t)opencfw_em9305_init_secondary_compare_3249e8);
        if(inserted!=0u)return inserted;
    }
}
