#ifndef R1_NATIVE_HRV_TIMING_H
#define R1_NATIVE_HRV_TIMING_H
#include <stdint.h>
struct r1_hrv_timing_state {
    uint8_t mode, flag1, flag2, reserved;
    uint32_t stream, field8, hr_timer, timer;
};
extern volatile struct r1_hrv_timing_state r1_hrv_timing_state;
extern uint8_t r1_hrv_session_buffer[208];
void r1_hrv_timing_start_plan(uint32_t);
void r1_hrv_stream_release(void);
void r1_hrv_producer(uint32_t,const volatile void *,uint32_t);
#endif
