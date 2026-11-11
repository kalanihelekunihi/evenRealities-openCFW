/* Stock 0x9338c/0x933b4 share the request at 0x2000680c. Cold bytes are
 * authenticated by executing native scatter decode; command is retained.
 * See touch-request-c-review.md. All executed operations are C. */
#include <stddef.h>
#include "native_touch_transport.h"
extern generic_device_registry_device *volatile r1_touch_bus_device;
_Static_assert(sizeof(uintptr_t)==4 && sizeof(generic_device_registry_request_block)==20,"native request ABI");
_Static_assert(offsetof(generic_device_registry_request_block,code)==2 && offsetof(generic_device_registry_request_block,buffer)==4 && offsetof(generic_device_registry_request_block,length)==8 && offsetof(generic_device_registry_request_block,data)==12 && offsetof(generic_device_registry_request_block,length2)==16,"native request offsets");
volatile generic_device_registry_request_block r1_touch_request
 __attribute__((section(".r1.touch.request"),aligned(4)))={.command=0x56,.length=1,.length2=1};
uint32_t r1_touch_request_read_native(uint32_t reg,void *data,uint32_t length)
{
 r1_touch_request.code=(uint16_t)reg;
 r1_touch_request.length2=(uint16_t)length;
 r1_touch_request.data=(uintptr_t)data;
 uint32_t status=r1_stock_dispatch_10(r1_touch_bus_device,0,(uintptr_t)&r1_touch_request,0);
 return status==0;
}
uint32_t r1_touch_request_write_native(uint32_t reg,const void *data,uint32_t length)
{
 r1_touch_request.code=(uint16_t)reg;
 r1_touch_request.length=(uint16_t)length;
 /* Stock clears the pointer on NULL; unlike the separate I2C5 adapter. */
 r1_touch_request.buffer=(uintptr_t)data;
 uint32_t status=r1_stock_dispatch_14(r1_touch_bus_device,0,(uintptr_t)&r1_touch_request,0);
 return status==0;
}

#include "native_touch_ready_state.h"
/* Stock 0x933dc reads the input-ready byte. The C API returns that byte;
 * unused scratch bytes and caller-clobbered register values are private. */
__attribute__((noinline)) uint32_t r1_touch_ready_level_read(void)
{
 volatile uint32_t word=0;
 (void)r1_stock_dispatch_10(r1_touch_input_device,0,(uintptr_t)&word,0);
 return ((volatile uint8_t *)&word)[0];
}

/* Stock IQS register-port shims. Forward the complete input words; the
 * canonical request functions apply their own native 16-bit field widths. */
uint32_t r1_iqs7211e_register_read_port(uint32_t address,uint32_t reg,void *data,
                                     uint32_t length,uint32_t option)
{
 (void)address;(void)option;
 return r1_touch_request_read_native(reg,data,length);
}
uint32_t r1_iqs7211e_register_write_port(uint32_t address,uint32_t reg,const void *data,
                                      uint32_t length,uint32_t option)
{
 (void)address;(void)option;
 return r1_touch_request_write_native(reg,data,length);
}
