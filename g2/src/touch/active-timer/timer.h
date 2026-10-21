#ifndef TOUCH_ACTIVE_TIMER_OFFLINE_H
#define TOUCH_ACTIVE_TIMER_OFFLINE_H
#include <stdint.h>
/* Independent stock5d90 active timer setter and6bd4 active-slot launch. */
uint32_t touch_set_active_interval(uint32_t microseconds,uint8_t *context);
uint32_t touch_start_active_slots(uint32_t first,uint32_t count,uint8_t *context);
/* State1 successful-processing tail3d7e; proven no-op logging omitted. */
void touch_active_budget_step(uint8_t *state,uint32_t *budget,uint8_t *context);
#endif
