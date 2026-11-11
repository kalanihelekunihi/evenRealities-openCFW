#ifndef R1_NATIVE_HEALTH_HR_TIMING_H
#define R1_NATIVE_HEALTH_HR_TIMING_H
#include <stdint.h>
void r1_hr_timing_timer_callback(uint32_t);
void r1_hr_timing_result_plan(uint32_t,const volatile void *,uint32_t);
void r1_algo_hr_timing_timeout(uint32_t);
#endif
