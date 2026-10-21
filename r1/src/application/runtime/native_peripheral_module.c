#include <stdint.h>
#include "../registry/stock_registry.h"
extern void r1_led_ldo_device_bind(void);
extern void r1_i2c5_nfc_resource_registration(void);
extern void r1_yhm_device_handles_initialize(void);
extern generic_device_registry_device *r1_native_rtc_cached_device(void);
extern uint32_t r1_native_watchdog_hw_handle_init(void);
/* The remaining numeric routes retain their recovered caller role. Actual
 * callee bodies/argument-register liveness remain explicit integration gates. */
extern void r1_vbat_adc_handle_cache(void);
extern void r1_ppg_device_bind(void);
extern void r1_motion_interrupt_input_lookup(void);
extern void r1_touch_device_bind(void);
extern void r1_i2c2_handle_cache(void);
void r1_peripheral_module_init(void)
{
 r1_led_ldo_device_bind();
 (void)r1_native_rtc_cached_device();
 r1_vbat_adc_handle_cache();
 r1_yhm_device_handles_initialize();
 r1_ppg_device_bind();
 r1_motion_interrupt_input_lookup();
 r1_touch_device_bind();
 r1_i2c2_handle_cache();
 r1_i2c5_nfc_resource_registration();
 (void)r1_native_watchdog_hw_handle_init();
}
