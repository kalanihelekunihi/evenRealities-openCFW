#ifndef R1_NATIVE_TEMPERATURE_STATE_H
#define R1_NATIVE_TEMPERATURE_STATE_H
#include <stdint.h>
struct r1_temperature_mode_control {
    uint8_t mode, reserved[3];
    uint32_t timer;
};
extern volatile struct r1_temperature_mode_control r1_temperature_mode_control;
extern volatile uint32_t r1_temperature_mode_handles[3];
extern volatile uint8_t r1_temperature_timing_record[14];
extern volatile uint8_t r1_temperature_sleep_capture[106];
void r1_temperature_mode_set(uint32_t);
void r1_temperature_stream_sample_callback(uint32_t,uint32_t,uint32_t);
#endif
