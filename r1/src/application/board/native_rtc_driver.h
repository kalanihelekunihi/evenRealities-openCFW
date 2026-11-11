#ifndef R1_NATIVE_RTC_DRIVER_H
#define R1_NATIVE_RTC_DRIVER_H
#include <stdint.h>
#include "nrfx_rtc.h"
uint32_t r1_rtc_driver_initialize(const void *,const void *,nrfx_rtc_handler_t);
void r1_rtc_driver_tick_enable(const void *,uint32_t);
void r1_rtc_driver_enable(const void *);
/* Shared product error logger returns; it does not reset or halt. */
void r1_adc_error(uint32_t);
#endif
