#ifndef TOUCH_CLOCK_SELECTION_OFFLINE_H
#define TOUCH_CLOCK_SELECTION_OFFLINE_H
#include <stdint.h>
uint32_t touch_poly_period(uint32_t);
uint32_t touch_dither_value(uint32_t,uint32_t);
uint32_t touch_dither_limit(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t touch_ssc_run(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t touch_prs_auto(const uint8_t *,const uint8_t *);
uint32_t touch_ssc_auto(const uint8_t *,const uint8_t *);
uint32_t touch_lfsr_auto(const uint8_t *,const uint8_t *);
uint32_t touch_initialize_source_clock(uint8_t *);
uint32_t touch_timer_cycles(uint32_t,const uint8_t *);
#endif
