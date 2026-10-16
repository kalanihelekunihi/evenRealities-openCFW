/* Typed SDK boundary for the recovered 8-byte native instance/config prefix. */
#include <stddef.h>
#include "nrfx_rtc.h"
#include "native_rtc_driver.h"
_Static_assert(sizeof(nrfx_rtc_t)==8 && offsetof(nrfx_rtc_t,irq)==4 && offsetof(nrfx_rtc_t,instance_id)==5 && offsetof(nrfx_rtc_t,cc_channel_count)==6,"native RTC instance ABI");
_Static_assert(sizeof(nrfx_rtc_config_t)<=8 && offsetof(nrfx_rtc_config_t,interrupt_priority)==2 && offsetof(nrfx_rtc_config_t,tick_latency)==3 && offsetof(nrfx_rtc_config_t,reliable)==4,"native RTC configuration ABI");
uint32_t r1_rtc_driver_initialize(const void *instance,const void *config,void (*handler)(uint32_t)) {
    return nrfx_rtc_init(instance,config,(nrfx_rtc_handler_t)handler);
}
void r1_rtc_driver_tick_enable(const void *instance,uint32_t enabled) {
    nrfx_rtc_tick_enable(instance,enabled!=0);
}
void r1_rtc_driver_enable(const void *instance) {nrfx_rtc_enable(instance);}
