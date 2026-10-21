#ifndef TOUCH_MODE_OFFLINE_H
#define TOUCH_MODE_OFFLINE_H
#include <stdint.h>
typedef struct {
 void (*ios)(uint8_t *);void (*shield)(uint8_t *);void (*cmod)(uint8_t *);
 uint32_t (*configure)(volatile uint32_t *,const void *,uint32_t,void *);
 void (*auto_dither)(uint8_t *);
} touch_mode_dependencies;
uint32_t touch_wait_mrss(uint32_t,uint32_t,uint8_t *);
void touch_cpu_operating(uint8_t *);
void touch_saturation_mode(uint8_t *);
uint32_t touch_switch_mode(uint32_t,uint8_t *,const touch_mode_dependencies *);
uint32_t touch_switch_saturation_dependency(uint32_t,uint8_t *);
uint32_t touch_cap_init_fields(uint8_t *);
/* Independent full initializer and default capture, using pinned public PDL. */
uint32_t touch_capture_default(uint8_t *);
uint32_t touch_cap_init(uint8_t *);
uint32_t touch_switch_regular_dependency(uint32_t,uint8_t *);

#endif
