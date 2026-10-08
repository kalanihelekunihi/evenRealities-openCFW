#ifndef TOUCH_LP_SCAN_OFFLINE_H
#define TOUCH_LP_SCAN_OFFLINE_H
#include <stdint.h>
/* Independent stock6d74. Stable coherent ARM32 contexts; offline only. */
uint32_t touch_start_lp_slots(uint32_t first,uint32_t count,uint8_t *context);
#endif
