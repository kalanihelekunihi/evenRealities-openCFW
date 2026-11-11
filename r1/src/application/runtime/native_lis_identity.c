#include <stdint.h>
#include <stddef.h>
#include "native_lis_context.h"
struct generic_device_registry_device;
extern struct generic_device_registry_device *volatile r1_motion_bus_device;
extern uint32_t r1_stock_dispatch_10(struct generic_device_registry_device *,uintptr_t,uintptr_t,uintptr_t);
extern uint32_t r1_stock_dispatch_14(struct generic_device_registry_device *,uintptr_t,uintptr_t,uintptr_t);
/* Every native request byte is owned, including the zero-filled reserved
 * fields. Explicit padding keeps aggregate initialization deterministic. */
struct r1_motion_bus_request {
 uint8_t address, reserved1;
 uint16_t reg;
 uint32_t write_pointer;
 uint16_t write_length, reserved2;
 uint32_t read_pointer;
 uint16_t read_length, reserved3;
};
_Static_assert(sizeof(uintptr_t)==4 && sizeof(struct r1_motion_bus_request)==20,
               "native motion request extent");
_Static_assert(offsetof(struct r1_motion_bus_request,reg)==2 &&
               offsetof(struct r1_motion_bus_request,write_pointer)==4 &&
               offsetof(struct r1_motion_bus_request,write_length)==8 &&
               offsetof(struct r1_motion_bus_request,read_pointer)==12 &&
               offsetof(struct r1_motion_bus_request,read_length)==16 &&
               offsetof(struct r1_motion_bus_request,reserved3)==18,
               "native motion request offsets");
uint32_t r1_motion_bus_read_request(uint32_t address, uint32_t reg,
                                   uint8_t *data, uint32_t length)
{
 struct r1_motion_bus_request request = {0};
 request.reg = (uint16_t)reg;
 request.address = (uint8_t)address;
 request.read_length = (uint16_t)length;
 request.read_pointer = (uintptr_t)data;
 return r1_stock_dispatch_10(r1_motion_bus_device,0,(uintptr_t)&request,0)==0;
}
uint32_t r1_motion_bus_write_request(uint32_t address, uint32_t reg,
                                    const uint8_t *data, uint32_t length)
{
 struct r1_motion_bus_request request = {0};
 request.reg = (uint16_t)reg;
 request.address = (uint8_t)address;
 request.write_pointer = (uintptr_t)data;
 request.write_length = (uint16_t)length;
 return r1_stock_dispatch_14(r1_motion_bus_device,0,(uintptr_t)&request,0)==0;
}
int32_t r1_lis_default_read(void *handle __attribute__((unused)),
                            uint8_t reg, uint8_t *data, uint16_t length)
{
 (void)r1_motion_bus_read_request(24, reg, data, length);
 return 0;
}
int32_t r1_lis_default_write(void *handle __attribute__((unused)),
                             uint8_t reg, const uint8_t *data, uint16_t length)
{
 (void)r1_motion_bus_write_request(24, reg, data, length);
 return 0;
}
int32_t r1_lis_device_id_get(const stmdev_ctx_t *ctx, uint8_t *identity)
{
 return lis2dw12_read_reg(ctx, 0x0f, identity, 1);
}
uint32_t r1_lis2dw12_identity_probe(void)
{
 volatile struct r1_lis_context_prefix *live = &r1_lis_context;
 if (!live->write)
  live->write = r1_lis_default_write;
 if (!live->read)
  live->read = r1_lis_default_read;
 uint8_t identity = 0;
 (void)r1_lis_device_id_get((const stmdev_ctx_t *)&r1_lis_context, &identity);
 return identity;
}
