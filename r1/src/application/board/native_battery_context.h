#ifndef R1_NATIVE_BATTERY_CONTEXT_H
#define R1_NATIVE_BATTERY_CONTEXT_H
#include <stdint.h>
#include <stddef.h>
struct generic_device_registry_device;
/* One C storage owner for each native context. Byte consumers and typed
 * status/ADC views share the same union representation on the ARM target. */
struct r1_battery_device_fields {
 uint8_t prefix[44],status2c,status2d,tail[22];
};
union r1_battery_device_store {
 uint8_t bytes[68];
 struct r1_battery_device_fields fields;
 uint32_t alignment;
};
struct r1_battery_runtime_fields {
 uint8_t prefix[16];
 struct generic_device_registry_device *adc;
 uint8_t bytes20_43[24];
 uint16_t cadence[4][6];
};
union r1_battery_runtime_store {
 uint8_t bytes[92];
 struct r1_battery_runtime_fields fields;
 uint32_t alignment;
};
_Static_assert(sizeof(union r1_battery_device_store)==68 &&
 _Alignof(union r1_battery_device_store)==4 &&
 offsetof(struct r1_battery_device_fields,status2c)==44 &&
 offsetof(struct r1_battery_device_fields,status2d)==45,"native device views");
_Static_assert(sizeof(union r1_battery_runtime_store)==92 &&
 _Alignof(union r1_battery_runtime_store)==4 &&
 offsetof(struct r1_battery_runtime_fields,adc)==16 &&
 offsetof(struct r1_battery_runtime_fields,cadence)==44,"native runtime views");
extern volatile union r1_battery_device_store r1_battery_device_storage;
extern volatile union r1_battery_runtime_store r1_battery_runtime_storage;
#define r1_battery_device_context (r1_battery_device_storage.bytes)
#define r1_battery_runtime_context (r1_battery_runtime_storage.bytes)
#define r1_device_state_byte_2c (r1_battery_device_storage.fields.status2c)
#define r1_device_state_byte_2d (r1_battery_device_storage.fields.status2d)
#define r1_vbat_adc_device (r1_battery_runtime_storage.fields.adc)
#endif
