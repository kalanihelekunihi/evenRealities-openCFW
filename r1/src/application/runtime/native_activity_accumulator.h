#ifndef R1_NATIVE_ACTIVITY_ACCUMULATOR_H
#define R1_NATIVE_ACTIVITY_ACCUMULATOR_H
#include <stdint.h>
extern volatile uint8_t r1_activity_accumulator_state[24];
void r1_activity_accumulator_latest_copy(volatile void *output);
void r1_activity_periodic_accumulator(volatile void *);
#endif
