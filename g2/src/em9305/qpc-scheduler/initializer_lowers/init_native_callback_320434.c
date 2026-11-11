#include <stdint.h>

/* Native 0x320434..0x320540: stream control event callback. Event kinds
 * 6/5/2 map to stream modes 1/2/2 (kind 2 also bumps 0x803561); others
 * are passed through. The mode goes to 320540 for the addressed stream
 * object, or for every object enabled in 0x803560 when the handle (+0)
 * or index (+2) is 0xff or the mode is 1/2. Then kind 1 (re)configures
 * the scan ring (0x80356c) and the two timers at 0x8035bc/0x8035cc with
 * the periods at +8/+12 (kept at 0x8035b4/0x8035b8), kind 6 restarts
 * them, kind 2 stops them, and kind 3 finishes through 30e910 once both
 * the counter and the second period are clear. */
extern uint32_t opencfw_em9305_child_320540(uintptr_t object, uint32_t mode);
extern uint32_t opencfw_em9305_scan_ring_init_316a54(uintptr_t ring, uint32_t enable);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer, uint32_t milliseconds);
extern uint32_t opencfw_em9305_child_30e910(void);
extern uint8_t *const opencfw_em9305_stream_objects_3357b4[3];

void opencfw_em9305_callback_320434(uintptr_t event)
{
    volatile uint8_t *control=(volatile uint8_t *)(uintptr_t)0x803560u;
    volatile uint32_t *periods=(volatile uint32_t *)(uintptr_t)0x8035b4u;
    const uintptr_t first_timer=0x8035bcu,second_timer=0x8035ccu;
    uint32_t kind=*(volatile uint8_t *)(event+3u);
    uint32_t mode=kind;
    if(kind==6u)mode=1u;
    else if(kind==5u)mode=2u;
    else if(kind==2u){
        control[1]=(uint8_t)(control[1]+1u);
        mode=2u;
    }
    uint32_t handle=*(volatile uint16_t *)event;
    uint32_t enabled=control[0];
    if(handle!=255u&&mode-1u>=2u&&*(volatile uint8_t *)(event+2u)!=255u){
        if(((enabled>>(handle&31u))&1u)!=0u)
            (void)opencfw_em9305_child_320540((uintptr_t)opencfw_em9305_stream_objects_3357b4[handle],mode);
    }else{
        for(uint32_t index=0u;index<3u;++index){
            if(((enabled>>index)&1u)==0u)continue;
            (void)opencfw_em9305_child_320540((uintptr_t)opencfw_em9305_stream_objects_3357b4[index],mode);
            enabled=control[0];
        }
    }
    kind=*(volatile uint8_t *)(event+3u);
    if(kind==6u){
        if(control[9]==2u)(void)opencfw_em9305_scan_ring_init_316a54(0x80356cu,1u);
        (void)opencfw_em9305_wsf_timer_start_ms(first_timer,periods[0]);
        (void)opencfw_em9305_wsf_timer_start_ms(second_timer,periods[1]);
    }else if(kind==2u){
        (void)opencfw_em9305_wsf_timer_stop(first_timer);
        (void)opencfw_em9305_wsf_timer_stop(second_timer);
    }else if(kind==3u){
        if(control[1]!=0u||periods[1]!=0u)return;
        (void)opencfw_em9305_child_30e910();
    }else if(kind==1u){
        uint32_t scan=*(volatile uint8_t *)(event+4u);
        control[9]=(uint8_t)scan;
        control[1]=0u;
        (void)opencfw_em9305_scan_ring_init_316a54(0x80356cu,scan!=0u);
        (void)opencfw_em9305_wsf_timer_stop(first_timer);
        (void)opencfw_em9305_wsf_timer_stop(second_timer);
        uint32_t period=*(volatile uint32_t *)(event+8u);
        periods[0]=period;
        periods[1]=*(volatile uint32_t *)(event+12u);
        if(period==0u)return;
        (void)opencfw_em9305_wsf_timer_start_ms(first_timer,period);
        period=periods[1];
        if(period==0u)return;
        (void)opencfw_em9305_wsf_timer_start_ms(second_timer,period);
    }
}
