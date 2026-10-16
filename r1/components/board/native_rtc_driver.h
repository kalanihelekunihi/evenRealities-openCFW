#ifndef R1_NATIVE_RTC_DRIVER_H
#define R1_NATIVE_RTC_DRIVER_H
#include <stdint.h>
uint32_t r1_rtc_driver_initialize(const void *,const void *,void (*)(uint32_t));
void r1_rtc_driver_tick_enable(const void *,uint32_t);
void r1_rtc_driver_enable(const void *);
void r1_rtc_driver_error(uint32_t);
#endif
