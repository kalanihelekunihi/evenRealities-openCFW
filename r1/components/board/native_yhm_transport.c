#include <stdint.h>
#include "native_battery_memory.h"
#include "../registry/stock_registry.h"
extern volatile uint8_t r1_yhm_transport_context[];
extern volatile uint8_t r1_yhm_request[];
static generic_device_registry_device *bus(void)
{ return (void *)(uintptr_t)read32(r1_yhm_transport_context+4); }
uint32_t r1_yhm_transport_acquire(void)
{ return r1_stock_dispatch_08(bus()); }
uint32_t r1_yhm_transport_release(void)
{ return r1_stock_dispatch_0c((void *)(uintptr_t)read32(r1_yhm_transport_context+12)); }
uint32_t r1_yhm_transport_complete(void)
{
    uint32_t result=r1_stock_dispatch_0c(bus());
    uint32_t (*callback)(uint32_t)=(void *)(uintptr_t)read32(r1_yhm_transport_context);
    return callback ? callback(0) : result;
}
uint32_t r1_yhm_register_read_record(uint32_t reg,uint32_t length,uint8_t *data)
{
    (void)r1_yhm_transport_release();
    (void)r1_yhm_transport_acquire();
    r1_yhm_request[0]=(uint8_t)reg;
    write32(r1_yhm_request+12,(uintptr_t)data);
    r1_yhm_request[16]=(uint8_t)length;
    (void)r1_stock_dispatch_10(bus(),0,(uintptr_t)r1_yhm_request,0);
    return r1_yhm_transport_complete();
}
uint32_t r1_yhm_register_write_record(uint32_t reg,uint32_t length,const uint8_t *data)
{
    (void)r1_yhm_transport_release();
    (void)r1_yhm_transport_acquire();
    r1_yhm_request[0]=(uint8_t)reg;
    write32(r1_yhm_request+4,(uintptr_t)data);
    r1_yhm_request[8]=(uint8_t)length;
    (void)r1_stock_dispatch_14(bus(),0,(uintptr_t)r1_yhm_request,0);
    return r1_yhm_transport_complete();
}
uint32_t r1_yhm_register_write_native(uint32_t reg,uint32_t length,const uint8_t *data)
{ return r1_yhm_register_write_record(reg,(uint8_t)length,data); }
