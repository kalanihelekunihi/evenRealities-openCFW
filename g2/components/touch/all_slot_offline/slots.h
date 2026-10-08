#ifndef TOUCH_ALL_SLOT_OFFLINE_H
#define TOUCH_ALL_SLOT_OFFLINE_H
#include <stdint.h>
/* Locked compile-time layout:5 active slots,4 low-power slots; types0/1.
 * Per-sensor errors are discarded, matching stock. Coherent ARM32 pointers. */
void touch_generate_all_slots(uint32_t,uint8_t *);
#endif
