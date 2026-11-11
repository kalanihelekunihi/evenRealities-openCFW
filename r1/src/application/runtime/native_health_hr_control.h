#ifndef R1_NATIVE_HEALTH_HR_CONTROL_H
#define R1_NATIVE_HEALTH_HR_CONTROL_H
#include <stdint.h>
void r1_hr_once_measurement_control(uint32_t,uint32_t);
void r1_hr_once_result_plan(uint32_t,const volatile void *,uint32_t);
uint32_t r1_hr_value_plausible(const volatile void *);
#endif
