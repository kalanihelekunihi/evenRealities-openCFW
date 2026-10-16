/* Native 0x54d20. Signed rejection and wrapping table addressing are deliberate:
 * negative commands pass the native comparison and are not silently guarded. */
#include <stdint.h>
#include "../registry/stock_registry.h"
typedef void (*r1_output_metadata_fn)(void);
typedef struct {
 const char *name;uint8_t opened,padding[3];uint32_t pin;
 uint8_t config_0c,config_0d,config_0e,config_0f;uint32_t config_10,reserved_14[3];
 generic_device_registry_device device;
} r1_output_gpio_record;
typedef struct {r1_output_gpio_record records[5];r1_output_metadata_fn driver[6],ops[9];} r1_output_gpio_configuration;
extern r1_output_gpio_configuration r1_output_gpio;
extern int strcmp(const char *,const char *);
extern void r1_rtt_delay_cycles(uint32_t);
_Static_assert(sizeof(r1_output_gpio_record)==56 && offsetof(r1_output_gpio_configuration,driver)==280,"native table offsets");
uint32_t r1_output_gpio_slot18(volatile generic_device_registry_device *device,uint32_t command) {
 if((int32_t)command>=3)return 1;
 for(uint8_t i=0;i<5;++i){
  volatile r1_output_gpio_record *record=&r1_output_gpio.records[i];
  if(strcmp(record->name,device->name)!=0)continue;
  if(!record->opened)return 27;
  uint32_t delayed=record->config_0d!=0;
  uintptr_t address=(uintptr_t)&r1_output_gpio+280u+(delayed?12u:0u)+(command<<2);
  uintptr_t target=*(const volatile uintptr_t *)address;
  ((void (*)(volatile r1_output_gpio_record *))target)(record);
  if(delayed)r1_rtt_delay_cycles(64000);
  return 0;
 }
 return 1;
}
