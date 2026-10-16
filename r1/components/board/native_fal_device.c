/* Native R1 FAL-to-device-registry adapter, not an upstream FAL body. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <fal.h>
#include "../registry/stock_registry.h"
generic_device_registry_device *volatile r1_fal_device_handle __attribute__((section(".r1.fal.device_handle")));
struct request { uint32_t first,offset,bytes; };
struct request r1_fal_write_request __attribute__((section(".r1.fal.write_request")));
struct request r1_fal_read_request __attribute__((section(".r1.fal.read_request")));
struct geometry { uint8_t pages,reserved[3];uint32_t base,reserved8,page_size; };
struct geometry r1_fal_geometry __attribute__((section(".r1.fal.geometry")));
int r1_native_fal_device_initialize(void);
int r1_native_fal_device_read(long,uint8_t *,size_t);
int r1_native_fal_device_write(long,const uint8_t *,size_t);
int r1_native_fal_device_erase(long,size_t);
struct fal_flash_dev r1_fal_flash_device __attribute__((section(".r1.fal.device_record")))={
 "device_flash",0,0,0,{r1_native_fal_device_initialize,r1_native_fal_device_read,r1_native_fal_device_write,r1_native_fal_device_erase},32
};
_Static_assert(sizeof(struct fal_flash_dev)==56,"native FAL device extent");
_Static_assert(offsetof(struct fal_flash_dev,ops.read)==40 && offsetof(struct fal_flash_dev,ops.erase)==48,"native FAL operation slots");
_Static_assert(sizeof(struct request)==12 && sizeof(struct geometry)==16,"native request/geometry extent");
int r1_native_fal_device_initialize(void)
{
 generic_device_registry_device *device=r1_stock_registry_find("device_flash");
 r1_fal_device_handle=device;(void)r1_stock_dispatch_00(device);
 if (!r1_stock_dispatch_18(r1_fal_device_handle,1,(uintptr_t)&r1_fal_geometry)) {
  r1_fal_flash_device.addr=r1_fal_geometry.base;
  uint32_t pages=r1_fal_geometry.pages,size=r1_fal_geometry.page_size;
  r1_fal_flash_device.len=pages*size;r1_fal_flash_device.blk_size=size;
 }
 return 1;
}
int r1_native_fal_device_read(long offset,uint8_t *destination,size_t bytes)
{
 r1_fal_read_request.first=(uint32_t)(uintptr_t)destination;
 r1_fal_read_request.offset=offset;r1_fal_read_request.bytes=bytes;
 (void)r1_stock_dispatch_10(r1_fal_device_handle,0,(uintptr_t)&r1_fal_read_request,0);
 return bytes;
}
int r1_native_fal_device_write(long offset,const uint8_t *source,size_t bytes)
{
 r1_fal_write_request.first=(uint32_t)(uintptr_t)source;
 r1_fal_write_request.offset=offset;r1_fal_write_request.bytes=bytes;
 if (!bytes) r1_fal_write_request.bytes=(uint32_t)strlen((const char *)source);
 return r1_stock_dispatch_14(r1_fal_device_handle,0,(uintptr_t)&r1_fal_write_request,0);
}
int r1_native_fal_device_erase(long offset,size_t bytes)
{
 r1_fal_write_request.first=0;r1_fal_write_request.offset=offset;r1_fal_write_request.bytes=bytes;
 return r1_stock_dispatch_18(r1_fal_device_handle,0,(uintptr_t)&r1_fal_write_request);
}
