/* Hardware TWI register adapters use ordinary C status/argument ABIs. */
#include "nrfx_twim.h"
#include "../registry/stock_registry.h"
#include "native_hw_twi.h"
#include "native_hw_twi_legacy_tx.h"
extern uint32_t r1_twi_primary_wait_adapter(uint32_t),r1_twi_secondary_wait_adapter(uint32_t);
extern void r1_adc_error(uint32_t);
/* Ordinary C status ABI: register-byte TX, first wait, RX, final wait.
 * Scratch-register returns and private frame overlays are not API outputs. */
uint32_t r1_twi_primary_register_read_adapter(uint32_t address,uint32_t reg,void *output,uint32_t length,const void *instance)
{
    volatile uint32_t command=length;
    *(volatile uint8_t *)&command=(uint8_t)reg;
    volatile uint8_t *control=(volatile uint8_t *)&r1_hw_twi0.control;
    control[0]=0;control[1]=0;
    uint32_t result=r1_twi_primary_legacy_tx(instance,(uint8_t)address,(const void *)(uintptr_t)&command,1,true);
    if (result) return (uint8_t)result;
    result=r1_twi_primary_wait_adapter(500);
    if (result) return (uint8_t)result;
    control[0]=0;
    result=nrfx_twim_rx((const void *)((uintptr_t)instance+4),(uint8_t)address,output,(uint8_t)length);
    if (result) return (uint8_t)result;
    return (uint8_t)r1_twi_primary_wait_adapter(length<50?200:500);
}
uint32_t r1_twi_secondary_register_read_adapter(uint32_t address,uint32_t reg,void *output,uint32_t length,const void *instance)
{
    volatile uint32_t command=length;
    *(volatile uint8_t *)&command=(uint8_t)reg;
    volatile uint8_t *control=(volatile uint8_t *)&r1_hw_twi1.control;
    control[0]=0;
    uint32_t result=r1_twi_secondary_legacy_tx(instance,(uint8_t)address,(const void *)(uintptr_t)&command,1,true);
    if (result) return (uint8_t)result;
    result=r1_twi_secondary_wait_adapter(100);
    if (result) return (uint8_t)result;
    control[0]=0;
    result=nrfx_twim_rx((const void *)((uintptr_t)instance+4),(uint8_t)address,output,length);
    if (result) return (uint8_t)result;
    return (uint8_t)r1_twi_secondary_wait_adapter(length<50?200:500);
}

/* Stock accepts 80 payload bytes plus one register byte. Allocate all 81
 * explicitly rather than overlapping a saved register at the boundary. */
__attribute__((always_inline)) static inline uint32_t write_register_c(uint32_t address,uint32_t reg,const volatile uint8_t *input,uint32_t length,const void *instance,uint32_t secondary)
{
 if (length>80) return 9;
 volatile uint8_t scratch[81];
 scratch[0]=(uint8_t)reg;
 for (uint32_t i=0;i<length;++i) scratch[i+1]=input[i];
 volatile r1_hw_twi_control *control=secondary?&r1_hw_twi1.control:&r1_hw_twi0.control;
 control->state_00=0;if (!secondary) control->state_01=0;
 for (;;) {
  uint32_t result=secondary?r1_twi_secondary_legacy_tx(instance,(uint8_t)address,(const void *)(uintptr_t)scratch,(uint8_t)(length+1),false):r1_twi_primary_legacy_tx(instance,(uint8_t)address,(const void *)(uintptr_t)scratch,(uint8_t)(length+1),false);
  if (result==17) return result;
  if (result) {r1_adc_error(result);continue;}
  result=secondary?r1_twi_secondary_wait_adapter(200):r1_twi_primary_wait_adapter(500);
  return (uint8_t)result;
 }
}
uint32_t r1_twi_primary_register_write_adapter(uint32_t a,uint32_t r,const void *p,uint32_t n,const void *i){return write_register_c(a,r,p,n,i,0);}
uint32_t r1_twi_secondary_register_write_adapter(uint32_t a,uint32_t r,const void *p,uint32_t n,const void *i){return write_register_c(a,r,p,n,i,1);}
