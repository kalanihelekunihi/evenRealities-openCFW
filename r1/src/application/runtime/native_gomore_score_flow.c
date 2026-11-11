#include <stdint.h>

extern void r1_gomore_interval_statistics_native(uint32_t,uint32_t,uint32_t,uint32_t,volatile void *);
extern void r1_gomore_stage_statistics_native(uint32_t,uint32_t,uint32_t,uint32_t,volatile void *);
extern float r1_gomore_sleep_score_native(const volatile void *);

void r1_gomore_dual_statistics_native(uint32_t data,uint32_t auxiliary,
        uint32_t duration,uint32_t reserved,volatile void *metrics)
{
    r1_gomore_interval_statistics_native(data,auxiliary,duration,reserved,metrics);
    volatile void *stages=(volatile void *)(uintptr_t)((uint32_t)(uintptr_t)metrics+28u);
    r1_gomore_stage_statistics_native(data,auxiliary,duration,reserved,stages);
}

void r1_gomore_prepare_score_native(uint32_t data,uint32_t auxiliary,
        uint32_t duration,uint32_t reserved,uint32_t unused_mode,
        volatile void *metrics,volatile float *score)
{
    (void)unused_mode;
    r1_gomore_dual_statistics_native(data,auxiliary,duration,reserved,metrics);
    float value=r1_gomore_sleep_score_native(metrics);
    *score=value;
}
