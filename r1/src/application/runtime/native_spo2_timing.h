#ifndef R1_NATIVE_SPO2_TIMING_H
#define R1_NATIVE_SPO2_TIMING_H
#include <stdint.h>
struct r1_spo2_timing_state {
    uint8_t mode,flag1,flag2,reserved;
    uint32_t timer;
};
extern volatile struct r1_spo2_timing_state r1_spo2_timing_state;
extern volatile uint32_t r1_spo2_streams[3];
void r1_stress_stream_release(void);
void r1_spo2_timing_start_plan(uint32_t);
void r1_spo2_timing_timeout(uint32_t);
void r1_spo2_timing_sample(uint32_t,const volatile void *,uint32_t);
#endif
