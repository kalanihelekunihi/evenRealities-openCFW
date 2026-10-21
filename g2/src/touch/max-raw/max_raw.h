#ifndef TOUCH_MAX_RAW_OFFLINE_H
#define TOUCH_MAX_RAW_OFFLINE_H
#include <stdint.h>
uint32_t touch_saturated_max(uint32_t fifo,uint32_t scan_ctl,uint32_t clock_source,uint32_t method,uint32_t chop);
typedef uint32_t (*touch_saturated_scan)(uint32_t *,uint32_t,uint32_t,uint32_t,uint8_t *);
uint32_t touch_max_raw_init(uint32_t id,uint8_t *context,touch_saturated_scan scan);
#endif
