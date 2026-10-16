/* Native five-record output lifecycle and sixteen-byte predecessor table.
 * The table's final adjacency to r1_output_gpio is a linker placement gate.
 * Callback r0 is the callback address itself; other scratch residue is gated. */
#include "nrfx_gpiote.h"
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
extern void r1_adc_error(uint32_t);
_Static_assert(sizeof(r1_output_gpio_record)==56 && offsetof(r1_output_gpio_record,device)==32,"native record");
_Static_assert(sizeof(nrfx_gpiote_out_config_t)==3 && offsetof(nrfx_gpiote_out_config_t,init_state)==1 && offsetof(nrfx_gpiote_out_config_t,task_pin)==2,"native short-enum output config");
void r1_output_gpio_task_initialize(volatile r1_output_gpio_record *record) {
 if(!nrfx_gpiote_is_init()){
  uint32_t status=nrfx_gpiote_init();if(status)r1_adc_error(status);
 }
 uint32_t status=nrfx_gpiote_out_init(record->pin,(const nrfx_gpiote_out_config_t *)((uintptr_t)record+14));
 if(status)r1_adc_error(status);
 nrfx_gpiote_out_task_enable(record->pin);
 if(record->config_0c)nrfx_gpiote_out_set(record->pin);else nrfx_gpiote_out_clear(record->pin);
}
void r1_output_gpio_task_release(volatile r1_output_gpio_record *record) {
 nrfx_gpiote_out_task_disable(record->pin);nrfx_gpiote_out_uninit(record->pin);
}
void r1_output_gpio_direct_initialize(volatile r1_output_gpio_record *record) {
 nrf_gpio_cfg(record->pin,NRF_GPIO_PIN_DIR_OUTPUT,NRF_GPIO_PIN_INPUT_DISCONNECT,NRF_GPIO_PIN_NOPULL,NRF_GPIO_PIN_S0S1,NRF_GPIO_PIN_NOSENSE);
 if(record->config_0c)nrf_gpio_pin_set(record->pin);else nrf_gpio_pin_clear(record->pin);
}
void r1_output_gpio_direct_release(volatile r1_output_gpio_record *record) {
 nrf_gpio_cfg(record->pin,NRF_GPIO_PIN_DIR_INPUT,NRF_GPIO_PIN_INPUT_DISCONNECT,NRF_GPIO_PIN_NOPULL,NRF_GPIO_PIN_S0S1,NRF_GPIO_PIN_NOSENSE);
}
typedef void (*r1_output_lifecycle_fn)(volatile r1_output_gpio_record *);
r1_output_lifecycle_fn r1_output_gpio_lifecycle[4] __attribute__((section(".r1.output_gpio.lifecycle")))={
 r1_output_gpio_task_initialize,r1_output_gpio_direct_initialize,r1_output_gpio_task_release,r1_output_gpio_direct_release
};
static volatile r1_output_gpio_record *find_record(volatile generic_device_registry_device *device) {
 for(uint8_t i=0;i<5;++i){volatile r1_output_gpio_record *record=&r1_output_gpio.records[i];if(strcmp(record->name,device->name)==0)return record;}
 return 0;
}
static void dispatch(volatile r1_output_gpio_record *record,uint32_t release) {
 uintptr_t address=(uintptr_t)r1_output_gpio_lifecycle+(release?8u:0u)+((uint32_t)record->config_0d<<2);
 uintptr_t target=*(const volatile uintptr_t *)address;
 ((r1_output_lifecycle_fn)target)(record);
}
uint32_t r1_output_gpio_open(volatile generic_device_registry_device *device) {
 volatile r1_output_gpio_record *record=find_record(device);if(!record)return 1;
 if(record->opened)return 0;
 if(*(volatile uint8_t *)&record->reserved_14[0]){
  uintptr_t target=record->reserved_14[1];if(target)((void (*)(uintptr_t))target)(target);
 }
 dispatch(record,0);record->opened=1;return 0;
}
uint32_t r1_output_gpio_close(volatile generic_device_registry_device *device) {
 volatile r1_output_gpio_record *record=find_record(device);if(!record)return 1;
 if(!record->opened)return 0;
 uint32_t callback=*(volatile uint8_t *)&record->reserved_14[0] && record->reserved_14[2];
 dispatch(record,1);
 if(callback){uintptr_t target=record->reserved_14[2];((void (*)(uintptr_t))target)(target);}
 record->opened=0;return 0;
}
