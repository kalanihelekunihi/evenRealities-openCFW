/* Native register adapters. SDK driver/RTOS bodies stay pinned providers.
 * Frames preserve native register byte placement and saved r2/r3 words. */
#include "nrfx_twim.h"
#include "../registry/stock_registry.h"
typedef void (*r1_hw_metadata_fn)(void);
typedef struct {uint8_t state_00,state_01,state_02,padding;void *semaphore;uint32_t reserved_08;} r1_hw_twi_control;
typedef struct {
 const char *name;uint8_t opened,padding[3];uint32_t pin_08,pin_0c,instance_id;
 uintptr_t peripheral;uint32_t driver_index,use_dma;r1_hw_metadata_fn irq;
 generic_device_registry_device device;r1_hw_metadata_fn ops[9];
} r1_hw_twi_record;
typedef struct {r1_hw_twi_control control;r1_hw_twi_record record;} r1_hw_twi_cluster;
extern r1_hw_twi_cluster r1_hw_twi0,r1_hw_twi1;
extern uint32_t r1_twi_primary_wait_adapter(uint32_t),r1_twi_secondary_wait_adapter(uint32_t);
extern void r1_adc_error(uint32_t);
static uint32_t read_register(uint32_t address,uint32_t reg,void *output,uint32_t length,const void *instance,volatile uint32_t *frame,uint32_t secondary) {
 volatile r1_hw_twi_control *control=secondary?&r1_hw_twi1.control:&r1_hw_twi0.control;
 ((volatile uint8_t *)frame)[4]=(uint8_t)reg;
 control->state_00=0;if(!secondary)control->state_01=0;
 frame[0]=1;
 const nrfx_twim_t *twim=(const void *)((uintptr_t)instance+4);
 uint32_t result=nrfx_twim_tx(twim,(uint8_t)address,(const uint8_t *)(uintptr_t)(frame+1),1,true);
 if(result)return (uint8_t)result;
 result=secondary?r1_twi_secondary_wait_adapter(100):r1_twi_primary_wait_adapter(500);
 if(result)return (uint8_t)result;
 control->state_00=0;
 result=nrfx_twim_rx(twim,(uint8_t)address,output,secondary?length:(uint8_t)length);
 if(result)return (uint8_t)result;
 result=secondary?r1_twi_secondary_wait_adapter(length<50?200:500):r1_twi_primary_wait_adapter(length<50?200:500);
 return (uint8_t)result;
}
__attribute__((used,noinline)) static uint32_t read0(uint32_t a,uint32_t r,void *p,uint32_t n,const void *i,volatile uint32_t *f){return read_register(a,r,p,n,i,f,0);}
__attribute__((used,noinline)) static uint32_t read1(uint32_t a,uint32_t r,void *p,uint32_t n,const void *i,volatile uint32_t *f){return read_register(a,r,p,n,i,f,1);}
#define READ_BRIDGE(name,kernel) \
__attribute__((naked,noinline)) uint32_t name(uint32_t a __attribute__((unused)),uint32_t r __attribute__((unused)),void *p __attribute__((unused)),uint32_t n __attribute__((unused)),const void *i __attribute__((unused))) { \
 __asm__ volatile("push {r2,r3,r4,r5,r6,r7,r8,r9,r10,lr}\nmov r12,sp\nsub sp,sp,#8\nstr r12,[sp,#4]\nldr r12,[sp,#48]\nstr r12,[sp]\nbl " #kernel "\nadd sp,sp,#8\npop {r2,r3,r4,r5,r6,r7,r8,r9,r10,pc}"); }
READ_BRIDGE(r1_twi_primary_register_read_adapter,read0)
READ_BRIDGE(r1_twi_secondary_register_read_adapter,read1)
static uint32_t write_register(uint32_t address,uint32_t reg,const volatile uint8_t *input,uint32_t length,const void *instance,volatile uint32_t *frame,uint32_t secondary) {
 if(length>80)return 9;
 volatile uint8_t *buffer=(volatile uint8_t *)(frame+1);buffer[0]=(uint8_t)reg;
 for(uint8_t i=0;i<length;++i)buffer[i+1]=input[i];
 volatile r1_hw_twi_control *control=secondary?&r1_hw_twi1.control:&r1_hw_twi0.control;
 control->state_00=0;if(!secondary)control->state_01=0;
 for(;;){
  frame[0]=0;
  uint32_t result=nrfx_twim_tx((const void *)((uintptr_t)instance+4),(uint8_t)address,(const uint8_t *)(uintptr_t)buffer,(uint8_t)(length+1),false);
  if(result==17)return result;
  if(result){r1_adc_error(result);continue;}
  result=secondary?r1_twi_secondary_wait_adapter(200):r1_twi_primary_wait_adapter(500);
  return (uint8_t)result;
 }
}
__attribute__((used,noinline)) static uint32_t write0(uint32_t a,uint32_t r,const volatile uint8_t *p,uint32_t n,const void *i,volatile uint32_t *f){return write_register(a,r,p,n,i,f,0);}
__attribute__((used,noinline)) static uint32_t write1(uint32_t a,uint32_t r,const volatile uint8_t *p,uint32_t n,const void *i,volatile uint32_t *f){return write_register(a,r,p,n,i,f,1);}
#define WRITE_BRIDGE(name,kernel) \
__attribute__((naked,noinline)) uint32_t name(uint32_t a __attribute__((unused)),uint32_t r __attribute__((unused)),const void *p __attribute__((unused)),uint32_t n __attribute__((unused)),const void *i __attribute__((unused))) { \
 __asm__ volatile("push {r4,r5,r6,r7,lr}\nsub sp,sp,#84\nmov r12,sp\nsub sp,sp,#8\nstr r12,[sp,#4]\nldr r12,[sp,#112]\nstr r12,[sp]\nbl " #kernel "\nadd sp,sp,#92\npop {r4,r5,r6,r7,pc}"); }
WRITE_BRIDGE(r1_twi_primary_register_write_adapter,write0)
WRITE_BRIDGE(r1_twi_secondary_register_write_adapter,write1)
