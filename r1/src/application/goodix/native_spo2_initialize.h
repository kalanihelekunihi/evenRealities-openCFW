#ifndef R1_GOODIX_NATIVE_SPO2_INITIALIZE_H
#define R1_GOODIX_NATIVE_SPO2_INITIALIZE_H
#include <stdint.h>
uint32_t r1_goodix_spo2_session_initialize(const void *,void *);
uint32_t r1_goodix_spo2_short_pair_initialize(const void *,void *);
uint32_t r1_goodix_spo2_initialize_session_channel(const void *,void *);
uint32_t r1_goodix_native_extended_s16_queue_initialize(void *,void *,uint32_t,uint32_t);
uint32_t r1_goodix_native_float_record_initialize(void *,void *,uint32_t,uint32_t);
uint32_t r1_goodix_native_s16_queue_initialize(void *,void *,uint32_t);
#endif
