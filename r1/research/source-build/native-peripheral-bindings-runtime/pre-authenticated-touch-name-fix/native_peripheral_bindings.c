/* Native product handle caches. Only the accessed four-byte cells are owned;
 * surrounding motion/PPG/touch contexts retain independent ownership gates. */
#include "../registry/stock_registry.h"
#define TEXT(name,sec,value) const char name[] __attribute__((section(sec)))=value
/* Separate cells avoid claiming the intervening context fields. */
#define HANDLE(name) generic_device_registry_device *volatile name __attribute__((section(".r1.bind." #name),aligned(4)))=0
HANDLE(r1_led_enable_device);HANDLE(r1_touch_ldo_device);
HANDLE(r1_motion_irq_device);HANDLE(r1_motion_bus_device);
HANDLE(r1_ppg_bus_device);HANDLE(r1_ppg_irq_device);HANDLE(r1_ppg_reset_device);
HANDLE(r1_touch_bus_device);HANDLE(r1_touch_input_device);HANDLE(r1_touch_output_device);
#undef HANDLE
TEXT(r1_bind_motion_irq_name,".r1.bind.name0","acc_int_1");
TEXT(r1_bind_motion_bus_name,".r1.bind.name1","i2c_1");
TEXT(r1_bind_led_name,".r1.bind.name2","ppg_led_en");
TEXT(r1_bind_ldo_name,".r1.bind.name3","touch_ldo_en");
TEXT(r1_bind_ppg_bus_name,".r1.bind.name4","i2c_4");
TEXT(r1_bind_ppg_irq_name,".r1.bind.name5","ppg_int");
TEXT(r1_bind_ppg_reset_name,".r1.bind.name6","ppg_reset_en");
TEXT(r1_bind_touch_bus_name,".r1.bind.name7","i2c_0");
TEXT(r1_bind_touch_input_name,".r1.bind.name8","touch_rdy_in");
TEXT(r1_bind_touch_output_name,".r1.bind.name9","touch_rdy_out");
uintptr_t r1_led_ldo_device_bind(void) {
 if(!r1_led_enable_device)r1_led_enable_device=r1_stock_registry_find(r1_bind_led_name);
 generic_device_registry_device *result=r1_touch_ldo_device;
 if(!result){result=r1_stock_registry_find(r1_bind_ldo_name);r1_touch_ldo_device=result;}
 return (uintptr_t)result;
}
uintptr_t r1_motion_bus_device_bind(void) {
 generic_device_registry_device *result=r1_motion_bus_device;
 if(!result){result=r1_stock_registry_find(r1_bind_motion_bus_name);r1_motion_bus_device=result;}
 return (uintptr_t)result;
}
uintptr_t r1_motion_interrupt_input_lookup(void) {
 (void)r1_motion_bus_device_bind();
 generic_device_registry_device *result=r1_motion_irq_device;
 if(!result){result=r1_stock_registry_find(r1_bind_motion_irq_name);r1_motion_irq_device=result;}
 return (uintptr_t)result;
}
uint32_t r1_ppg_device_bind(void) {
 if(!r1_ppg_bus_device)r1_ppg_bus_device=r1_stock_registry_find(r1_bind_ppg_bus_name);
 if(!r1_ppg_irq_device)r1_ppg_irq_device=r1_stock_registry_find(r1_bind_ppg_irq_name);
 generic_device_registry_device *result=r1_ppg_reset_device;
 if(!result){result=r1_stock_registry_find(r1_bind_ppg_reset_name);r1_ppg_reset_device=result;}
 return r1_stock_dispatch_08(result);
}
uintptr_t r1_touch_device_bind(void) {
 if(!r1_touch_bus_device)r1_touch_bus_device=r1_stock_registry_find(r1_bind_touch_bus_name);
 if(!r1_touch_input_device)r1_touch_input_device=r1_stock_registry_find(r1_bind_touch_input_name);
 generic_device_registry_device *result=r1_touch_output_device;
 if(!result){result=r1_stock_registry_find(r1_bind_touch_output_name);r1_touch_output_device=result;}
 return (uintptr_t)result;
}
