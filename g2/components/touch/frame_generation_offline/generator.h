#ifndef TOUCH_FRAME_GENERATION_OFFLINE_H
#define TOUCH_FRAME_GENERATION_OFFLINE_H
#include <stdint.h>
void touch_frame_mask(uint32_t,uint32_t,uint32_t *);
uint32_t touch_adjust_divider(uint8_t,uint8_t,uint16_t);
typedef uint32_t (*touch_cdac_generator)(const uint8_t *,uint32_t *,const uint8_t *);
/* CDAC is an explicit open dependency; active frame7 words, LP11 words.
 * Nonzero frame types select LP slot table; only type1 emits LP prefix. */
uint32_t touch_generate_sensor(uint32_t,uint32_t,uint32_t *,const uint8_t *,touch_cdac_generator);
uint32_t touch_generate_cdac(const uint8_t *,uint32_t *,const uint8_t *);
uint32_t touch_generate_sensor_closed(uint32_t,uint32_t,uint32_t *,const uint8_t *);
#endif
