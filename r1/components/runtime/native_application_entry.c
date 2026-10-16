#include <stdint.h>
typedef uint32_t (*timestamp_function)(void);
extern uint32_t nrf_log_init(timestamp_function,uint32_t);
extern void nrf_log_default_backends_init(void);
extern void cm_backtrace_init(const char *,const char *,const char *);
extern uint32_t ble_dfu_buttonless_async_svci_init(void);
extern uint32_t nrf_drv_clock_init(void);
extern void r1_adc_error(uint32_t);
extern void r1_boot_ctor_run(void);
extern void r1_peripheral_module_init(void);
extern void r1_device_module_init(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void r1_reset_reason_nordic_adapter(void);
__attribute__((section(".r1.app.entry.version"),used))
const char r1_app_entry_version[12]="2.2.6.0009";
__attribute__((section(".r1.app.entry.hardware"),used))
const char r1_app_entry_hardware[12]="603MV1.9.3";
__attribute__((section(".r1.app.entry.build"),used))
const char r1_app_entry_build[44]="product/B210/app/_build/B210_Application";
__attribute__((section(".r1.app.entry.ring"),used))
const char r1_app_entry_ring[32]="[RING]====APP B210 START====\r\n";
__attribute__((section(".r1.app.entry.sdk"),used))
const char r1_app_entry_sdk[28]="====APP B210 START====\r\n";
__attribute__((section(".r1.app.entry.scr"),used))
const uint32_t r1_app_entry_scr=UINT32_C(0xe000ed10);
__attribute__((section(".r1.app.entry.log_bounds"),used))
const uint32_t r1_app_entry_log_bounds[2]={UINT32_C(0xc44fc),UINT32_C(0xc441c)};
__attribute__((section(".r1.app.entry.callback_cell"),used))
const uint32_t r1_app_entry_callback_cell=UINT32_C(0x20006540);
/* Descriptor callbacks, initialization state and all declared providers remain
 * explicit dependency/ABI gates until their source integration is verified. */
void r1_native_application_entry(void)
{
 volatile uint32_t *scr=(volatile uint32_t *)(uintptr_t)r1_app_entry_scr;
 *scr=*scr|4u;
 uint32_t status=nrf_log_init((timestamp_function)0,0x8000u);
 if(status)r1_adc_error(status);
 nrf_log_default_backends_init();
 cm_backtrace_init(r1_app_entry_build,r1_app_entry_hardware,r1_app_entry_version);
 status=ble_dfu_buttonless_async_svci_init();if(status)r1_adc_error(status);
 status=nrf_drv_clock_init();if(status)r1_adc_error(status);
 r1_boot_ctor_run();r1_peripheral_module_init();r1_device_module_init();
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c000000u,r1_app_entry_ring,r1_app_entry_ring);
 if(r1_structured_log_mode_get()&2u){
  uint32_t header=(((r1_app_entry_log_bounds[0]-r1_app_entry_log_bounds[1])>>3)<<16)+3u;
  nrf_log_frontend_std_0(header,r1_app_entry_sdk);
 }
 r1_reset_reason_nordic_adapter();
 ((void (*)(void))(uintptr_t)*(const volatile uint32_t *)(uintptr_t)r1_app_entry_callback_cell)();
 for(;;)r1_adc_error(15u);
}
