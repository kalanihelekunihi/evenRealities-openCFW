#ifndef TOUCH_PROXIMITY_OFFLINE_H
#define TOUCH_PROXIMITY_OFFLINE_H
#include <stdint.h>
void touch_raw_filters(const uint8_t *widget,uint8_t *sensor,uint16_t *history,uint8_t *fraction);
void touch_proximity_process(uint8_t *widget);
uint32_t touch_proximity_raw(uint32_t id,const uint8_t *context);
#endif
