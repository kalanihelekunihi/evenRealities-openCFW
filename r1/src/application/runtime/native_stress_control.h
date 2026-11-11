#ifndef R1_NATIVE_STRESS_CONTROL_H
#define R1_NATIVE_STRESS_CONTROL_H
#include <stdint.h>
struct r1_stress_mode_control {uint8_t mode,reserved[3];uint32_t timer;};
extern volatile struct r1_stress_mode_control r1_stress_mode_control;
uint32_t r1_stress_enable(uint32_t,uint32_t);
void r1_stress_mode_timer_plan(uint32_t,uint32_t);
void r1_stress_mode_set(uint32_t,uint32_t);
void r1_stress_periodic_timer_callback(uint32_t);
#endif
