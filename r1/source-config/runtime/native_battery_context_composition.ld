SECTIONS {
 .r1.battery.device : {
  r1_battery_device_context = .;
  *(.r1.battery.device.prefix)
  *(.r1.status.device2c)
  *(.r1.status.device2d)
  *(.r1.battery.device.tail)
 }
 .r1.battery.runtime : {
  r1_battery_runtime_context = .;
  *(.r1.battery.runtime.prefix)
  *(.r1.vbat.cache)
  *(.r1.battery.runtime.tail)
 }
}
INSERT AFTER .data;
ASSERT(SIZEOF(.r1.battery.device)==68,"battery device extent")
ASSERT(SIZEOF(.r1.battery.runtime)==92,"battery runtime extent")
ASSERT(r1_device_state_byte_2c-r1_battery_device_context==44,"device2c alias")
ASSERT(r1_device_state_byte_2d-r1_battery_device_context==45,"device2d alias")
ASSERT(r1_vbat_adc_device-r1_battery_runtime_context==16,"ADC cache alias")
