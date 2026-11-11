#ifndef R1_NATIVE_TOUCH_TASK_CONTROL_H
#define R1_NATIVE_TOUCH_TASK_CONTROL_H
#include <stdint.h>
#include <stddef.h>
struct r1_touch_task_parameters { uint8_t first,reserved;uint16_t second;uint8_t third,fourth; };
struct r1_touch_factory_parameters { uint8_t marker,first,second,reserved3;uint16_t reserved4,half;uint32_t word; };
_Static_assert(sizeof(struct r1_touch_task_parameters)==6 && offsetof(struct r1_touch_task_parameters,second)==2,"native task parameters");
_Static_assert(sizeof(struct r1_touch_factory_parameters)==12 && offsetof(struct r1_touch_factory_parameters,half)==6 && offsetof(struct r1_touch_factory_parameters,word)==8,"native factory fields");
extern volatile uint8_t r1_touch_task_active,r1_touch_slider_flag;
extern volatile struct r1_touch_task_parameters r1_touch_parameters;
extern volatile struct r1_touch_factory_parameters r1_touch_factory_state;
#endif
