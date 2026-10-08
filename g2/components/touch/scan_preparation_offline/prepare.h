#ifndef TOUCH_SCAN_PREPARATION_OFFLINE_H
#define TOUCH_SCAN_PREPARATION_OFFLINE_H
#include <stdint.h>
uint32_t touch_dither_measure(const uint32_t *,const uint8_t *,uint32_t,uint32_t *,uint8_t *);
uint32_t touch_dither_scale(uint8_t *);
uint32_t touch_prepare_scan_fields(uint8_t *);
uint32_t touch_prepare_scan(uint8_t *);
#endif
