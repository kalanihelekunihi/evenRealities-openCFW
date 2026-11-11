#ifndef R1_GOODIX_STREAM_CALLBACKS_H
#define R1_GOODIX_STREAM_CALLBACKS_H
#include <stdint.h>
extern volatile uint8_t r1_goodix_stream_cache[240];
extern volatile uint32_t r1_goodix_stream_callbacks[8];
#define DECL_SETTER(s) uint32_t r1_stream_cfg_set_##s(uint32_t)
DECL_SETTER(00);DECL_SETTER(04);DECL_SETTER(08);DECL_SETTER(0c);
DECL_SETTER(10);DECL_SETTER(14);DECL_SETTER(18);DECL_SETTER(1c);
#undef DECL_SETTER
uint32_t r1_goodix_adt_append(uint32_t),r1_goodix_raw_hr_append(uint32_t);
uint32_t r1_goodix_stream_gain(const volatile void *,const volatile void *,const volatile void *);
uint32_t r1_goodix_stream_gray(const volatile void *,const volatile void *,const volatile void *);
uint32_t r1_goodix_stream_hr(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_goodix_stream_aging(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_goodix_stream_spo2(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_goodix_wear_living_object_update(uint32_t);
#endif
