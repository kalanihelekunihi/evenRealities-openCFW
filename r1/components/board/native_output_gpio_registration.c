/* Native five-record registrar0x54e78. Config-byte roles remain explicit by
 * offset; operation/driver references are metadata, not admitted body ABIs. */
#include <stdint.h>
#include "../registry/stock_registry.h"
typedef void (*r1_output_metadata_fn)(void);
extern void r1_output_gpio_low(void),r1_output_gpio_high(void),r1_output_gpio_toggle(void),r1_output_gpio_driver0c(void),r1_output_gpio_driver10(void),r1_output_gpio_driver14(void);
extern void r1_output_gpio_open(void),r1_output_gpio_close(void),r1_output_gpio_slot10(void),r1_output_gpio_slot18(void),r1_output_gpio_slot1c(void);
typedef struct {
 const char *name;uint8_t opened,padding[3];uint32_t pin;
 uint8_t config_0c,config_0d,config_0e,config_0f;uint32_t config_10,reserved_14[3];
 generic_device_registry_device device;
} r1_output_gpio_record;
typedef struct {r1_output_gpio_record records[5];r1_output_metadata_fn driver[6],ops[9];} r1_output_gpio_configuration;
_Static_assert(sizeof(r1_output_gpio_record)==56 && offsetof(r1_output_gpio_record,device)==32,"native GPIO record");
_Static_assert(sizeof(r1_output_gpio_configuration)==340 && offsetof(r1_output_gpio_configuration,ops)==304,"native GPIO configuration");
const char r1_output_gpio_name0[] __attribute__((section(".r1.output_gpio.name0")))="ppg_led_en";
const char r1_output_gpio_name1[] __attribute__((section(".r1.output_gpio.name1")))="touch_ldo_en";
const char r1_output_gpio_name2[] __attribute__((section(".r1.output_gpio.name2")))="ppg_reset_en";
const char r1_output_gpio_name3[] __attribute__((section(".r1.output_gpio.name3")))="ship_mode_en";
const char r1_output_gpio_name4[] __attribute__((section(".r1.output_gpio.name4")))="touch_rdy_out";
#define RECORD(n,p,c) {.name=n,.pin=p,.config_0c=c,.config_0d=1,.config_0e=3,.config_10=1}
r1_output_gpio_configuration r1_output_gpio __attribute__((section(".r1.output_gpio.configuration")))={
 .records={RECORD(r1_output_gpio_name0,10,0),RECORD(r1_output_gpio_name1,30,0),RECORD(r1_output_gpio_name2,36,0),RECORD(r1_output_gpio_name3,9,0),RECORD(r1_output_gpio_name4,17,1)},
 .driver={r1_output_gpio_low,r1_output_gpio_high,r1_output_gpio_toggle,r1_output_gpio_driver0c,r1_output_gpio_driver10,r1_output_gpio_driver14},
 .ops={[2]=r1_output_gpio_open,[3]=r1_output_gpio_close,[4]=r1_output_gpio_slot10,[6]=r1_output_gpio_slot18,[7]=r1_output_gpio_slot1c}
};
uint32_t r1_native_output_gpio_registration(void) {
 uint32_t status=0;
 for (uint8_t i=0;i<5;++i) {
  r1_output_gpio_record *record=&r1_output_gpio.records[i];
  record->device.name=record->name;record->device.ops=(const void *)r1_output_gpio.ops;
  status=r1_stock_registry_register(&record->device);
 }
 return status;
}
