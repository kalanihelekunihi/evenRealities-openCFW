#include <stdint.h>

/* Native 0x322a30..0x322b6e: stream reset callback. When the LL stream
 * gate is closed defer to 3227a4. Otherwise stop the running (state 2)
 * timers at +60/+20 of each of the three stream objects enabled in
 * 0x8019f8, then for each of the six 784-byte stream records at 0x803d7e
 * in state 2 (+30): release an unowned record (+0 clear) at +10 and, when
 * it carries a pending 0x2c completion (+404, +403), report LL event 0x32
 * with its parameters; finally return the record to state 0. */
extern uint32_t opencfw_em9305_ll_stream_gate_30e510(void);
extern void opencfw_em9305_callback_3227a4(void);
extern uint32_t opencfw_em9305_stream_stop_30e7ec(uintptr_t timer);
extern uint32_t opencfw_em9305_stream_release_30e834(uintptr_t stream);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
extern uint8_t *const opencfw_em9305_stream_objects_3357b4[3];

struct opencfw_em9305_event_32 {
    uint16_t handle;
    uint16_t code;
    uint16_t handle_again;
    uint8_t b6, b7;
    uint16_t h8;
    uint8_t b10, b11, b12;
    uint16_t h14;
    uint32_t w16;
    uint16_t h20;
    uint8_t b22, b23, b24;
};

void opencfw_em9305_callback_322a30(void)
{
    if(opencfw_em9305_ll_stream_gate_30e510()==0u){
        opencfw_em9305_callback_3227a4();
        return;
    }
    for(uint32_t index=0u;index<3u;++index){
        if(((*(volatile uint8_t *)(uintptr_t)0x8019f8u>>index)&1u)==0u)continue;
        uintptr_t object=(uintptr_t)opencfw_em9305_stream_objects_3357b4[index];
        if(*(volatile uint8_t *)(object+96u)==2u){
            (void)opencfw_em9305_stream_stop_30e7ec(object+60u);
            *(volatile uint8_t *)(object+96u)=0u;
        }
        if(*(volatile uint8_t *)(object+56u)==2u){
            (void)opencfw_em9305_stream_stop_30e7ec(object+20u);
            *(volatile uint8_t *)(object+56u)=0u;
        }
    }
    for(uint32_t index=0u;index<6u;++index){
        uintptr_t stream=0x803d7eu+index*784u;
        volatile uint8_t *s=(volatile uint8_t *)stream;
        if(s[30]!=2u)continue;
        if(s[0]==0u){
            (void)opencfw_em9305_stream_release_30e834(stream+10u);
            if(s[404]!=0u&&s[403]==0x2cu){
                struct opencfw_em9305_event_32 event;
                event.code=0x32u;
                event.b6=s[418];
                event.b7=s[419];
                event.h8=*(volatile uint16_t *)(stream+416u);
                event.b10=s[420];
                event.b11=s[426];
                event.b12=s[434];
                event.h14=*(volatile uint16_t *)(stream+436u);
                event.w16=*(volatile uint32_t *)(stream+442u);
                event.h20=*(volatile uint16_t *)(stream+446u);
                event.b22=s[458];
                event.b23=s[470];
                event.b24=s[471]!=0u;
                event.handle_again=(uint16_t)index;
                event.handle=(uint16_t)index;
                (void)opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
            }
        }
        s[30]=0u;
    }
}
