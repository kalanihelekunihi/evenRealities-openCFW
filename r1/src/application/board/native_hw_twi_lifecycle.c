/* Native TWI lifecycle in C. See twi-open-c-review.md for frame limits.
 * Legacy init sees the whole instance; nrfx enable/
 * disable/uninit see its embedded TWIM instance four bytes later. */
#include "nrf_drv_twi.h"
#include "../registry/stock_registry.h"
#include "native_hw_twi.h"
extern void r1_adc_error(uint32_t),r1_twi_gpio_output(uint32_t);
_Static_assert(sizeof(nrf_drv_twi_t)==16 && offsetof(nrf_drv_twi_t,u)==4 && offsetof(nrf_drv_twi_t,use_easy_dma)==12,"native legacy instance");
_Static_assert(sizeof(nrf_drv_twi_config_t)==16 && offsetof(nrf_drv_twi_config_t,interrupt_priority)==12 && offsetof(nrf_drv_twi_config_t,hold_bus_uninit)==14,"native config");
_Static_assert(NRF_DRV_TWI_FREQ_400K==0x06680000,"native frequency");
const uint32_t r1_hw_twi_template0[2] __attribute__((section(".r1.hw_twi.template0")))={0x06680000,0x00010002};
const uint32_t r1_hw_twi_template1[2] __attribute__((section(".r1.hw_twi.template1")))={0x06680000,0x00000002};
__attribute__((always_inline)) static inline uint32_t open_bus(volatile r1_hw_twi_cluster *cluster,volatile uint32_t *frame,uint32_t secondary){
 if(cluster->record.opened)return 0;
 volatile uint32_t *config=frame+(secondary?0:2);
 const uint32_t *tail=secondary?r1_hw_twi_template1:r1_hw_twi_template0;
 config[2]=tail[0];config[3]=tail[1];
 uint32_t first=cluster->record.pin_08;config[0]=first;config[1]=cluster->record.pin_0c;
 if(!secondary){
  frame[0]=0;frame[1]=0;r1_twi_gpio_output(first);
  frame[0]=0;frame[1]=0;r1_twi_gpio_output(cluster->record.pin_0c);
 }
 const nrf_drv_twi_t *instance=(const void *)((uintptr_t)&cluster->record+16);
 uint32_t result=nrf_drv_twi_init(instance,(const nrf_drv_twi_config_t *)(uintptr_t)config,(nrf_drv_twi_evt_handler_t)cluster->record.irq,0);
 if(result)r1_adc_error(result);
 nrfx_twim_enable(&instance->u.twim);cluster->record.opened=1;return 0;
}
/* Retain the native configuration window at caller SP-32 on both buses.
 * The final two secondary frame words preserve its surrounding envelope;
 * their contents are private and are not claimed identical. */
uint32_t r1_hw_twi0_open(void){volatile uint32_t frame[6];return open_bus(&r1_hw_twi0,frame,0);}
uint32_t r1_hw_twi1_open(void){volatile uint32_t frame[6];return open_bus(&r1_hw_twi1,frame,1);}
static uint32_t close_bus(volatile r1_hw_twi_cluster *cluster,uintptr_t power){
 if(!cluster->record.opened)return 0;
 const nrfx_twim_t *instance=(const void *)((uintptr_t)&cluster->record+20);
 nrfx_twim_disable(instance);nrfx_twim_uninit(instance);
 volatile uint32_t *reg=(volatile uint32_t *)power;
 *reg=0;(void)*reg;*reg=1;cluster->record.opened=0;return 0;
}
uint32_t r1_hw_twi0_close(void){return close_bus(&r1_hw_twi0,0x40003ffc);}
uint32_t r1_hw_twi1_close(void){return close_bus(&r1_hw_twi1,0x40004ffc);}
