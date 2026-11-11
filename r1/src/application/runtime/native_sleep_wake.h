#ifndef R1_NATIVE_SLEEP_WAKE_H
#define R1_NATIVE_SLEEP_WAKE_H
#include <stdint.h>
struct r1_sleep_wake_control {uint8_t active,reserved[3];uint32_t timer;};
extern volatile struct r1_sleep_wake_control r1_sleep_wake_control;
/* Native activity mode and sleep-active state are the same byte. */
#define r1_activity_mode (r1_sleep_wake_control.active)
void r1_algo_sleep_result_report(uint32_t);
extern volatile uint32_t r1_sleep_vivo_timer;
void r1_algo_sleep_vivo_probe_start(void);
void r1_sleep_vivo_probe_stop(uint32_t);
#endif
