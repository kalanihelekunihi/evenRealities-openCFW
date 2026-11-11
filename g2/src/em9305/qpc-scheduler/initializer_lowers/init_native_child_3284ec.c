#include <stdint.h>

/* Native 0x3284ec..0x328592: schedule the associated object. The window
 * is the floor at +2276 plus the scan window (at least 300) plus the
 * larger of +72 and the configured minimum (+20 of 0x805cac), capped at
 * 0x257ed4 and aligned by 312c5c. After initialising the object (seed
 * +76 unless +1432) at time +2272, it is inserted either at the latest
 * slot (step +836, 3130d4) or by adjustment (step +40, 312f88), moving
 * the time by one step after each refused attempt. */
extern uint32_t opencfw_em9305_scan_current_303f80(void);
extern uint32_t opencfw_em9305_channel_timing_adjust_312c5c(uint32_t window);
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t object, uint32_t seed);
extern uint32_t opencfw_em9305_init_schedule_latest_3130d4(uintptr_t object, uint32_t minimum,
                                                           uint32_t maximum);
extern uint32_t opencfw_em9305_init_schedule_adjust_312f88(uintptr_t object, uint32_t minimum,
                                                           uint32_t step);

uint32_t opencfw_em9305_child_3284ec(uintptr_t record, uintptr_t object)
{
    uint32_t floor=*(volatile uint32_t *)(record+2276u);
    uint32_t scan=opencfw_em9305_scan_current_303f80();
    scan=scan<301u?300u:opencfw_em9305_scan_current_303f80();
    volatile uintptr_t *config=(volatile uintptr_t *)(uintptr_t)0x805cacu;
    uint32_t minimum=*(volatile uint16_t *)(*config+20u);
    uint32_t requested=*(volatile uint32_t *)(record+72u);
    if(requested>minimum)minimum=requested;
    uint32_t window=minimum+floor+scan;
    window=opencfw_em9305_channel_timing_adjust_312c5c(window<0x257ed4u?window:0x257ed4u);
    uint32_t seed=0u;
    if(*(volatile uint8_t *)(record+1432u)==0u)seed=*(volatile uint8_t *)(record+76u);
    (void)opencfw_em9305_associated_object_init_312918(object,seed);
    volatile uint32_t *time=(volatile uint32_t *)(object+8u);
    uint32_t step=*(volatile uint32_t *)(record+836u);
    *time=*(volatile uint32_t *)(record+2272u);
    uint32_t status;
    if(step!=0u){
        while((status=opencfw_em9305_init_schedule_latest_3130d4(object,
                  *(volatile uint16_t *)(*config+22u)+window,step))==0u){
            step=*(volatile uint32_t *)(record+836u);
            *time+=step;
        }
    }else{
        step=*(volatile uint32_t *)(record+40u);
        for(;;){
            status=opencfw_em9305_init_schedule_adjust_312f88(object,
                       *(volatile uint16_t *)(*config+22u)+window,step);
            if(status!=0u)break;
            step=*(volatile uint32_t *)(record+40u);
            *time+=step;
        }
    }
    return status;
}
