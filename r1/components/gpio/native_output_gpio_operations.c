/* Native output GPIO operations; metadata declarations in the cold owner are
 * not an admitted operation prototype. No pin/backing-pointer guard is added. */
#include "nrf_gpio.h"
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
_Static_assert(sizeof(r1_output_gpio_record)==56 && offsetof(r1_output_gpio_record,device)==32,"native GPIO stride");
_Static_assert(sizeof(r1_output_gpio_configuration)==340 && offsetof(r1_output_gpio_configuration,ops)==304,"cold owner layout");
static volatile r1_output_gpio_record *find_record(volatile generic_device_registry_device *device) {
 for(uint8_t i=0;i<5;++i){
  volatile r1_output_gpio_record *record=&r1_output_gpio.records[i];
  if(strcmp(record->name,device->name)==0)return record;
 }
 return 0;
}
uint32_t r1_output_gpio_slot1c(volatile generic_device_registry_device *device,const volatile uint32_t *configuration) {
 if(!configuration)return 10;
 volatile r1_output_gpio_record *record=find_record(device);
 if(!record)return 1;
 /* Sequential reads/stores are deliberate, including overlapping storage. */
 *(volatile uint8_t *)&record->reserved_14[0]=*(const volatile uint8_t *)configuration;
 record->reserved_14[1]=configuration[1];
 record->reserved_14[2]=configuration[2];
 return 0;
}
/* Consume the attributable Nordic port decoder unchanged. Saved frame slots
 * retain native raw r3 results; helper stack history is still a separate gate. */
__attribute__((used,noinline)) static uintptr_t toggle_kernel(const volatile r1_output_gpio_record *record,uint32_t *saved_r3) {
 *saved_r3=record->pin;
 NRF_GPIO_Type *port=nrf_gpio_pin_port_decode(saved_r3);
 uint32_t out=port->OUT,mask=1u<<*saved_r3;
 port->OUTSET=mask&~out;port->OUTCLR=mask&out;
 return (uintptr_t)port;
}
__attribute__((naked,noinline)) uintptr_t r1_output_gpio_driver14(const void *record __attribute__((unused))) {
 __asm__ volatile("push {r3,lr}\nmov r1,sp\nbl toggle_kernel\npop {r3,pc}");
}
__attribute__((used,noinline)) static uint32_t read_kernel(volatile generic_device_registry_device *device,uint32_t ignored,volatile uint8_t *output,uint32_t *saved_r3) {
 (void)ignored;
 volatile r1_output_gpio_record *record=find_record(device);
 if(!record || !record->opened)return 1;
 *saved_r3=record->pin;
 NRF_GPIO_Type *port=nrf_gpio_pin_port_decode(saved_r3);
 *output=(uint8_t)((port->IN>>*saved_r3)&1u);
 return 0;
}
__attribute__((naked,noinline)) uint32_t r1_output_gpio_slot10(void *device __attribute__((unused)),uint32_t operation __attribute__((unused)),void *output __attribute__((unused))) {
 __asm__ volatile("push {r3,r4,r5,r6,r7,lr}\nmov r3,sp\nbl read_kernel\npop {r3,r4,r5,r6,r7,pc}");
}
