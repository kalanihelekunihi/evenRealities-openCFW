/* Native packet-operation adapters. Native saved-word frames are explicit;
 * composed register-adapter private stack placement remains independently gated. */
#include "nrfx_twim.h"
#include "../registry/stock_registry.h"
typedef void (*r1_hw_metadata_fn)(void);
typedef struct {uint8_t state_00,state_01,state_02,padding;void *semaphore;uint32_t reserved_08;} r1_hw_twi_control;
typedef struct {const char *name;uint8_t opened,padding[3];uint32_t pin_08,pin_0c,instance_id;uintptr_t peripheral;uint32_t driver_index,use_dma;r1_hw_metadata_fn irq;generic_device_registry_device device;r1_hw_metadata_fn ops[9];} r1_hw_twi_record;
typedef struct {r1_hw_twi_control control;r1_hw_twi_record record;} r1_hw_twi_cluster;
extern r1_hw_twi_cluster r1_hw_twi0,r1_hw_twi1;
extern uint32_t r1_twi_primary_register_read_adapter(uint32_t,uint32_t,void *,uint32_t,const void *),r1_twi_secondary_register_read_adapter(uint32_t,uint32_t,void *,uint32_t,const void *);
extern uint32_t r1_twi_primary_register_write_adapter(uint32_t,uint32_t,const void *,uint32_t,const void *),r1_twi_secondary_register_write_adapter(uint32_t,uint32_t,const void *,uint32_t,const void *);
extern uint32_t r1_twi_primary_wait_adapter(uint32_t),r1_twi_secondary_wait_adapter(uint32_t);
static uint32_t u16(const volatile uint8_t *p){return p[0]|((uint32_t)p[1]<<8);}
static uintptr_t u32(const volatile uint8_t *p){return p[0]|((uintptr_t)p[1]<<8)|((uintptr_t)p[2]<<16)|((uintptr_t)p[3]<<24);}
static uint32_t read_packet(const volatile uint8_t *request,volatile uint32_t *frame,uint32_t secondary){
 if(!request)return 9;
 volatile r1_hw_twi_cluster *cluster=secondary?&r1_hw_twi1:&r1_hw_twi0;
 if(!cluster->record.opened)return 8;
 const void *instance=(const void *)((uintptr_t)&cluster->record+16);frame[0]=(uintptr_t)instance;
 uint32_t length=secondary?request[16]:u16(request+16);
 uint32_t reg=secondary?request[2]:u16(request+2);
 void *output=(void *)u32(request+12);uint32_t address=request[0];
 uint32_t result=secondary?r1_twi_secondary_register_read_adapter(address,reg,output,length,instance):r1_twi_primary_register_read_adapter(address,reg,output,length,instance);
 return result?12:0;
}
static uint32_t write_packet(const volatile uint8_t *request,volatile uint32_t *frame,uint32_t secondary){
 if(!request)return 4;
 volatile r1_hw_twi_cluster *cluster=secondary?&r1_hw_twi1:&r1_hw_twi0;
 if(!cluster->record.opened)return 10;
 uint32_t length=u16(request+8);const void *instance=(const void *)((uintptr_t)&cluster->record+16);
 if(length!=1){
  frame[0]=(uintptr_t)instance;
  uint32_t reg=secondary?request[2]:u16(request+2);uint32_t address=request[0];const void *input=(const void *)u32(request+4);
  uint32_t result=secondary?r1_twi_secondary_register_write_adapter(address,reg,input,(uint8_t)length,instance):r1_twi_primary_register_write_adapter(address,reg,input,length,instance);
  return result?11:0;
 }
 const volatile uint8_t *input=(const void *)u32(request+4);
 uint32_t address=request[0],reg=request[2],value=input[0];
 volatile uint8_t *buffer=(volatile uint8_t *)(frame+1);buffer[0]=(uint8_t)reg;buffer[1]=(uint8_t)value;
 cluster->control.state_00=0;if(!secondary)cluster->control.state_01=0;frame[0]=0;
 uint32_t result=nrfx_twim_tx((const void *)((uintptr_t)instance+4),(uint8_t)address,(const uint8_t *)(uintptr_t)buffer,2,false);
 if(!result)result=secondary?r1_twi_secondary_wait_adapter(100):r1_twi_primary_wait_adapter(500);
 return (uint8_t)result?11:0;
}
__attribute__((used,noinline)) static uint32_t read0(uint32_t d,uint32_t o,const volatile uint8_t *r,volatile uint32_t *f){(void)d;(void)o;return read_packet(r,f,0);}
__attribute__((used,noinline)) static uint32_t read1(uint32_t d,uint32_t o,const volatile uint8_t *r,volatile uint32_t *f){(void)d;(void)o;return read_packet(r,f,1);}
__attribute__((used,noinline)) static uint32_t write0(uint32_t d,uint32_t o,const volatile uint8_t *r,volatile uint32_t *f){(void)d;(void)o;return write_packet(r,f,0);}
__attribute__((used,noinline)) static uint32_t write1(uint32_t d,uint32_t o,const volatile uint8_t *r,volatile uint32_t *f){(void)d;(void)o;return write_packet(r,f,1);}
#define READ(name,kernel) __attribute__((naked,noinline)) uint32_t name(uint32_t d __attribute__((unused)),uint32_t o __attribute__((unused)),const void *r __attribute__((unused))) {__asm__ volatile("push {r3,lr}\nmov r3,sp\nbl " #kernel "\npop {r3,pc}");}
#define WRITE(name,kernel) __attribute__((naked,noinline)) uint32_t name(uint32_t d __attribute__((unused)),uint32_t o __attribute__((unused)),const void *r __attribute__((unused))) {__asm__ volatile("push {r2,r3,r4,lr}\nmov r3,sp\nbl " #kernel "\npop {r2,r3,r4,pc}");}
READ(r1_hw_twi0_read,read0)
READ(r1_hw_twi1_read,read1)
WRITE(r1_hw_twi0_write,write0)
WRITE(r1_hw_twi1_write,write1)
