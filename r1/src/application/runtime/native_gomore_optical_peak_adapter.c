#include <stdint.h>
#include "gomore_primitives/gomore_primitives.h"
extern uint32_t r1_gomore_filter_configure_native(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_linear_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_filter_native(uint32_t,uint32_t,uint32_t);
static void configure(void *record,uint32_t rows,uint32_t columns,
                      const float parameters[2])
{
    (void)r1_gomore_filter_configure_native((uint32_t)(uintptr_t)record,
                                            rows,columns,
                                            (uint32_t)(uintptr_t)parameters);
}
static void resample(const float *source,int32_t input_count,int32_t output_count,
                     int32_t source_total,float *destination)
{
    (void)r1_gomore_linear_native((uint32_t)(uintptr_t)source,
                                  (uint32_t)input_count,(uint32_t)output_count,
                                  (uint32_t)source_total,
                                  (uint32_t)(uintptr_t)destination);
}
static void apply_filter(void *state,float *values,size_t count)
{
    (void)r1_gomore_filter_native((uint32_t)(uintptr_t)state,
                                  (uint32_t)(uintptr_t)values,(uint32_t)count);
}
uint32_t r1_gomore_stage_60af4_native(uint32_t state,uint32_t elapsed,
                                      uint32_t input,uint32_t output)
{
    (void)gomore_primitives_sleep_optical_peak_update(
        (gomore_primitives_sleep_optical_history *)(uintptr_t)state,
        elapsed,(const gomore_primitives_sleep_optical_input *)(uintptr_t)input,
        (uint8_t *)(uintptr_t)output,configure,resample,apply_filter);
    return 0;
}
