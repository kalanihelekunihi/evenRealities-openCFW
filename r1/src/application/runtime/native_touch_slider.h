#ifndef R1_NATIVE_TOUCH_SLIDER_H
#define R1_NATIVE_TOUCH_SLIDER_H
#include <stdint.h>
/* IQS callback: normalized flags, raw position, timestamp, opaque word,
 * and the mean sample pressure in S0 under the hard-float AAPCS. */
void r1_touch_slider_state_machine(uint32_t,uint32_t,uint32_t,uint32_t,float);
uint32_t r1_touch_slider_velocity_filter(uint32_t,uint32_t);
uint32_t r1_touch_release_debounce(uint32_t);
#endif
