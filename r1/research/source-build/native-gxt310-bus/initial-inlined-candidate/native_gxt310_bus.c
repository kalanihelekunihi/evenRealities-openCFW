#include <stdint.h>
#include <stddef.h>
#include "../registry/stock_registry.h"
typedef struct {
 uint8_t address,pad1;
 uint16_t reg;
 uint32_t write_pointer;
 uint16_t write_length,pad2;
 uint32_t read_pointer;
 uint16_t read_length;
} r1_gxt310_request;
typedef struct {generic_device_registry_device *device;r1_gxt310_request request;} r1_gxt310_bus_state;
_Static_assert(sizeof(uintptr_t)==4,"R1 pointer ABI");
_Static_assert(sizeof(r1_gxt310_request)==20,"request extent");
_Static_assert(offsetof(r1_gxt310_request,reg)==2 && offsetof(r1_gxt310_request,write_pointer)==4 && offsetof(r1_gxt310_request,write_length)==8 && offsetof(r1_gxt310_request,read_pointer)==12 && offsetof(r1_gxt310_request,read_length)==16,"native request offsets");
_Static_assert(offsetof(r1_gxt310_bus_state,request)==4 && sizeof(r1_gxt310_bus_state)==24,"native bus state layout");
__attribute__((section(".r1.gxt.bus.state"),aligned(4),used))
volatile r1_gxt310_bus_state r1_gxt310_i2c2_state={.device=0,.request={.address=0x12,.write_length=1,.read_length=1}};
__attribute__((section(".r1.gxt.bus.name"),used))
const char r1_gxt310_i2c2_name[8]="i2c_2";
void r1_i2c2_handle_cache(void)
{
 if(!r1_gxt310_i2c2_state.device)r1_gxt310_i2c2_state.device=r1_stock_registry_find(r1_gxt310_i2c2_name);
}
void r1_gxt310_bus_acquire(void){(void)r1_stock_dispatch_08(r1_gxt310_i2c2_state.device);}
void r1_gxt310_bus_release(void){(void)r1_stock_dispatch_0c(r1_gxt310_i2c2_state.device);}
uint32_t r1_gxt310_transfer_read_native(uint32_t address,uint32_t reg,uint8_t *data,uint32_t length)
{
 volatile r1_gxt310_request *p=&r1_gxt310_i2c2_state.request;
 p->reg=(uint16_t)reg;p->address=(uint8_t)address;p->read_length=(uint16_t)length;p->read_pointer=(uintptr_t)data;
 return r1_stock_dispatch_10(r1_gxt310_i2c2_state.device,0,(uintptr_t)p,0)==0;
}
uint32_t r1_gxt310_transfer_write_native(uint32_t address,uint32_t reg,const uint8_t *data,uint32_t length)
{
 volatile r1_gxt310_request *p=&r1_gxt310_i2c2_state.request;
 p->reg=(uint16_t)reg;p->address=(uint8_t)address;
 if(data)p->write_pointer=(uintptr_t)data;
 p->write_length=(uint16_t)length;
 return r1_stock_dispatch_14(r1_gxt310_i2c2_state.device,0,(uintptr_t)p,0)==0;
}
uint32_t r1_gxt310_register_read_native(uint32_t a,uint32_t r,uint8_t *p,uint32_t n){return r1_gxt310_transfer_read_native(a,r,p,n);}
uint32_t r1_gxt310_register_write_native(uint32_t a,uint32_t r,const uint8_t *p,uint32_t n){return r1_gxt310_transfer_write_native(a,r,p,n);}
