/* Hardware TWI packet operations use ordinary C status and argument ABIs. */
#include "nrfx_twim.h"
#include "../registry/stock_registry.h"
#include "native_hw_twi.h"
#include "native_hw_twi_legacy_tx.h"
#include "native_battery_memory.h"
extern uint32_t r1_twi_primary_register_read_adapter(uint32_t,uint32_t,void *,uint32_t,const void *),r1_twi_secondary_register_read_adapter(uint32_t,uint32_t,void *,uint32_t,const void *);
extern uint32_t r1_twi_primary_register_write_adapter(uint32_t,uint32_t,const void *,uint32_t,const void *),r1_twi_secondary_register_write_adapter(uint32_t,uint32_t,const void *,uint32_t,const void *);
extern uint32_t r1_twi_primary_wait_adapter(uint32_t),r1_twi_secondary_wait_adapter(uint32_t);
/* The read operation returns status only. The controller instance is an
 * ordinary fifth C argument; scratch-register restoration is not its result. */
__attribute__((always_inline)) static inline uint32_t packet_read_c(const volatile uint8_t *request,uint32_t secondary)
{
 if (!request) return 9;
 volatile r1_hw_twi_cluster *cluster=secondary?&r1_hw_twi1:&r1_hw_twi0;
 if (!cluster->record.opened) return 8;
 const void *instance=(const void *)((uintptr_t)&cluster->record+16);
 uint32_t length=secondary?request[16]:read16(request+16);
 uint32_t reg=secondary?request[2]:read16(request+2);
 void *output=(void *)(uintptr_t)read32(request+12);
 uint32_t address=request[0];
 uint32_t result=secondary?r1_twi_secondary_register_read_adapter(address,reg,output,length,instance):r1_twi_primary_register_read_adapter(address,reg,output,length,instance);
 return result?12:0;
}
uint32_t r1_hw_twi0_read(uint32_t device,uint32_t operation,const void *request){(void)device;(void)operation;return packet_read_c(request,0);}
uint32_t r1_hw_twi1_read(uint32_t device,uint32_t operation,const void *request){(void)device;(void)operation;return packet_read_c(request,1);}

/* Packet write returns status only; argument slots and scratch registers
 * are compiler-private. The short path transmits exactly two bytes. */
__attribute__((always_inline)) static inline uint32_t packet_write_c(const volatile uint8_t *request,uint32_t secondary)
{
    if (!request) return 4;
    volatile r1_hw_twi_cluster *cluster=secondary?&r1_hw_twi1:&r1_hw_twi0;
    if (!cluster->record.opened) return 10;
    uint32_t length=read16(request+8);
    const void *instance=(const void *)((uintptr_t)&cluster->record+16);
    if (length!=1) {
        uint32_t reg=secondary?request[2]:read16(request+2);
        uint32_t address=request[0];
        const void *input=(const void *)(uintptr_t)read32(request+4);
        uint32_t result=secondary?r1_twi_secondary_register_write_adapter(address,reg,input,(uint8_t)length,instance):r1_twi_primary_register_write_adapter(address,reg,input,length,instance);
        return result?11:0;
    }
    const volatile uint8_t *input=(const void *)(uintptr_t)read32(request+4);
    uint32_t address=request[0],reg=request[2];
    uint32_t value=input[0];
    volatile uint32_t command=(uint8_t)reg|((uint32_t)(uint8_t)value<<8);
    cluster->control.state_00=0;
    if (!secondary) cluster->control.state_01=0;
    uint32_t result=secondary?r1_twi_secondary_legacy_tx(instance,(uint8_t)address,(const void *)(uintptr_t)&command,2,false):r1_twi_primary_legacy_tx(instance,(uint8_t)address,(const void *)(uintptr_t)&command,2,false);
    if (!result) result=secondary?r1_twi_secondary_wait_adapter(100):r1_twi_primary_wait_adapter(500);
    return (uint8_t)result?11:0;
}
uint32_t r1_hw_twi0_write(uint32_t device,uint32_t operation,const void *request) {(void)device;(void)operation;return packet_write_c(request,0);}
uint32_t r1_hw_twi1_write(uint32_t device,uint32_t operation,const void *request) {(void)device;(void)operation;return packet_write_c(request,1);}
