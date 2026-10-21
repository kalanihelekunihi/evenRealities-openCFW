#include <stdint.h>
#include "../registry/stock_registry.h"
#include "../board/native_clock_bootstrap.h"
extern generic_device_registry_device *r1_structured_rtc_device;
extern void r1_device_preinitialize_3510c(void);
extern uint32_t r1_gxt310_self_check(void);
extern uint32_t r1_reset_reason_decode_and_report(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
__attribute__((section(".r1.device.startup.device_ring"),used))
const char r1_device_startup_device_ring[40]="[RING]device_module_application_init\r\n";
__attribute__((section(".r1.device.startup.device_sdk"),used))
const char r1_device_startup_device_sdk[36]="device_module_application_init\r\n";
__attribute__((section(".r1.device.startup.check_ring"),used))
const char r1_device_startup_check_ring[40]="[RING]temper hardware check error!!\r\n";
__attribute__((section(".r1.device.startup.check_sdk"),used))
const char r1_device_startup_check_sdk[32]="temper hardware check error!!\r\n";
__attribute__((section(".r1.device.startup.reset_ring"),used))
const char r1_device_startup_reset_ring[32]="[RING]RESETREAS raw = 0x%08x";
__attribute__((section(".r1.device.startup.reset_sdk"),used))
const char r1_device_startup_reset_sdk[24]="RESETREAS raw = 0x%08x";
__attribute__((section(".r1.device.startup.device_bounds"),used))
const uint32_t r1_device_startup_device_bounds[2]={UINT32_C(0xc44fc),UINT32_C(0xc441c)};
__attribute__((section(".r1.device.startup.check_state"),used))
const uint32_t r1_device_startup_check_state[1]={UINT32_C(0x20007684)};
__attribute__((section(".r1.device.startup.check_bounds"),used))
const uint32_t r1_device_startup_check_bounds[2]={UINT32_C(0xc44fc),UINT32_C(0xc441c)};
__attribute__((section(".r1.device.startup.rtc_cache"),used))
const uint32_t r1_device_startup_rtc_cache[1]={UINT32_C(0x20007690)};
__attribute__((section(".r1.device.startup.reset_register"),used))
const uint32_t r1_device_startup_reset_register[1]={UINT32_C(0x40000400)};
__attribute__((section(".r1.device.startup.reset_bounds"),used))
const uint32_t r1_device_startup_reset_bounds[2]={UINT32_C(0xc44fc),UINT32_C(0xc441c)};
__attribute__((section(".r1.device.startup.reset_cache"),used))
const uint32_t r1_device_startup_reset_cache[1]={UINT32_C(0x200064a8)};
/* Empty native callback is a supplemental body at0x4ea10. */
__attribute__((section(".r1.device.startup.rtc_noop"),noinline))
void r1_native_rtc_startup_tick_noop(uint32_t tick){(void)tick;}
__attribute__((section(".r1.device.startup.rtc_callback"),used))
r1_clock_tick_fn const r1_device_startup_rtc_callback=r1_native_rtc_startup_tick_noop;
void r1_device_init_thunk_4e9e8(void){r1_device_preinitialize_3510c();}
uint32_t r1_rtc_open_enable(void)
{
 (void)r1_stock_dispatch_08(r1_structured_rtc_device);
 return r1_stock_dispatch_20(r1_structured_rtc_device,0,(uintptr_t)r1_device_startup_rtc_callback);
}
static uint32_t log_header(const uint32_t bounds[2],uint32_t severity)
{
 return (((bounds[0]-bounds[1])>>3)<<16)+severity;
}
uint32_t r1_device_hardware_check_tail(void)
{
 volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)r1_device_startup_check_state[0];
 *state=0;
 if(r1_gxt310_self_check()==0){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   r1_structured_log_format(0x04000000u,r1_device_startup_check_ring,r1_device_startup_check_ring);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(log_header(r1_device_startup_check_bounds,1),r1_device_startup_check_sdk);
  volatile uint8_t *byte=(volatile uint8_t *)state;*byte=(uint8_t)(*byte|0x10u);
 }
 return 1;
}
void r1_device_module_init(void)
{
 r1_device_init_thunk_4e9e8();(void)r1_rtc_open_enable();
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c000000u,r1_device_startup_device_ring,r1_device_startup_device_ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(log_header(r1_device_startup_device_bounds,3),r1_device_startup_device_sdk);
 (void)r1_device_hardware_check_tail();
}
void r1_reset_reason_nordic_adapter(void)
{
 volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)r1_device_startup_reset_register[0];
 uint32_t raw=*reg;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c400000u,r1_device_startup_reset_ring,r1_device_startup_reset_ring,raw);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(log_header(r1_device_startup_reset_bounds,3),r1_device_startup_reset_sdk,raw);
 uint32_t decoded=r1_reset_reason_decode_and_report(raw);
 *(volatile uint32_t *)(uintptr_t)r1_device_startup_reset_cache[0]=decoded;
 *reg=raw;
}
