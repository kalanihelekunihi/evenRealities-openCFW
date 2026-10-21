/* Native R1 registered internal-flash policy; Nordic fstorage is the provider. */
#include <stdint.h>
#include <stddef.h>
#include "../registry/stock_registry.h"
#include <nrf_fstorage.h>
extern const nrf_fstorage_api_t nrf_fstorage_sd;
extern void r1_internal_flash_event_handler(nrf_fstorage_evt_t *);
extern void r1_adc_error(uint32_t);
extern uint32_t r1_internal_flash_page_erase(uint32_t,uint32_t);
extern void r1_internal_flash_mapped_read(void *,uint32_t,uint32_t);
extern uint32_t r1_internal_flash_word_write(const void *,uint32_t,uint32_t);
nrf_fstorage_t r1_internal_flash_context __attribute__((section(".r1.flash.fstorage")))={0,0,r1_internal_flash_event_handler,0,0};
const char r1_internal_flash_name[] __attribute__((section(".r1.flash.name"),aligned(1)))="device_flash";
struct native_flash_ops {
 uint32_t (*initialize)(generic_device_registry_device *);uint32_t reserved4,reserved8,reserved12;
 generic_device_registry_operation read,write;
 uint32_t (*control)(generic_device_registry_device *,uintptr_t,uintptr_t);
 uint32_t (*configure)(generic_device_registry_device *,uintptr_t);uint32_t reserved32;
};
struct native_flash_record {
 const char *name;volatile uint8_t initialized;uint8_t padding5[3];volatile uint8_t callbacks_enabled;uint8_t padding9[3];
 void (*volatile before)(void),(*volatile after)(void);
 generic_device_registry_device device;struct native_flash_ops ops;
};
uint32_t r1_internal_flash_callback_configuration(generic_device_registry_device *,uintptr_t);
uint32_t r1_internal_flash_fstorage_configuration(generic_device_registry_device *);
uint32_t r1_internal_flash_device_read(generic_device_registry_device *,uintptr_t,uintptr_t,uintptr_t);
uint32_t r1_internal_flash_device_write(generic_device_registry_device *,uintptr_t,uintptr_t,uintptr_t);
uint32_t r1_internal_flash_erase_and_geometry_control(generic_device_registry_device *,uintptr_t,uintptr_t);
struct native_flash_record r1_internal_flash_record __attribute__((section(".r1.flash.record")))={
 .name=r1_internal_flash_name,.ops={.initialize=r1_internal_flash_fstorage_configuration,.read=r1_internal_flash_device_read,.write=r1_internal_flash_device_write,.control=r1_internal_flash_erase_and_geometry_control,.configure=r1_internal_flash_callback_configuration}
};
_Static_assert(sizeof(struct native_flash_record)==80 && offsetof(struct native_flash_record,device)==20 && offsetof(struct native_flash_record,ops)==44,"native flash record");
_Static_assert(sizeof(nrf_fstorage_t)==20 && offsetof(nrf_fstorage_t,start_addr)==12,"SDK fstorage layout");
static uint32_t ficr_page_size(void) { return *(volatile uint32_t *)0x10000010; }
uint32_t r1_internal_flash_callback_configuration(generic_device_registry_device *device,uintptr_t input)
{
 (void)device;if (!input) return 11;
 const uint8_t *p=(const uint8_t *)input;
 r1_internal_flash_record.callbacks_enabled=*p;
 r1_internal_flash_record.before=*(void (*const *)(void))(p+4);
 r1_internal_flash_record.after=*(void (*const *)(void))(p+8);return 0;
}
uint32_t r1_internal_flash_fstorage_configuration(generic_device_registry_device *device)
{
 (void)device;if (r1_internal_flash_record.initialized) return 0;
 uint32_t boundary=*(volatile uint32_t *)0x10001014;
 (void)*(volatile uint32_t *)0x10001018;
 uint32_t page=ficr_page_size(),pages=*(volatile uint32_t *)0x10000014;
 uint32_t error=nrf_fstorage_init(&r1_internal_flash_context,&nrf_fstorage_sd,0);
 if (error) r1_adc_error(error);
 if (boundary==UINT32_MAX) boundary=pages*page;
 r1_internal_flash_context.start_addr=boundary-page*36u;r1_internal_flash_context.end_addr=boundary;
 r1_internal_flash_record.initialized=1;return 0;
}
struct transfer { void *buffer;uint32_t offset;uint16_t bytes; };
uint32_t r1_internal_flash_device_read(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra)
{
 (void)device;(void)operation;(void)extra;if (!request) return 26;
 if (!r1_internal_flash_record.initialized) return 27;
 struct transfer *p=(struct transfer *)request;
 if (r1_internal_flash_record.callbacks_enabled) {
  r1_internal_flash_record.before();r1_internal_flash_mapped_read(p->buffer,p->bytes,p->offset);r1_internal_flash_record.after();
 } else r1_internal_flash_mapped_read(p->buffer,p->bytes,p->offset);
 return 0;
}
uint32_t r1_internal_flash_device_write(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra)
{
 (void)device;(void)operation;(void)extra;if (!request) return 26;
 if (!r1_internal_flash_record.initialized) return 28;
 struct transfer *p=(struct transfer *)request;uint32_t result;
 if (r1_internal_flash_record.callbacks_enabled) {
  r1_internal_flash_record.before();result=r1_internal_flash_word_write(p->buffer,p->bytes,p->offset);r1_internal_flash_record.after();
 } else result=r1_internal_flash_word_write(p->buffer,p->bytes,p->offset);
 return result ? 0:21;
}
uint32_t r1_internal_flash_erase_and_geometry_control(generic_device_registry_device *device,uintptr_t operation,uintptr_t request)
{
 (void)device;if (!r1_internal_flash_record.initialized) return 27;
 if (operation==0) {
  if (!request) return 26;
  const uint32_t *p=(const uint32_t *)request;
  if (r1_internal_flash_record.callbacks_enabled) { r1_internal_flash_record.before();(void)r1_internal_flash_page_erase(p[1],p[2]);r1_internal_flash_record.after(); }
  else (void)r1_internal_flash_page_erase(p[1],p[2]);
  return 0;
 }
 if (operation!=1) return 25;
 if (!request) return 26;
 uint8_t *p=(uint8_t *)request;uint32_t page=ficr_page_size();
 *(uint32_t *)(p+8)=r1_internal_flash_context.end_addr;
 *(uint32_t *)(p+4)=r1_internal_flash_context.start_addr;
 *(uint32_t *)(p+12)=page;*p=36;return 0;
}
uint32_t r1_internal_flash_device_registration(void)
{
 r1_internal_flash_record.device.name=r1_internal_flash_record.name;
 r1_internal_flash_record.device.ops=(const generic_device_registry_ops *)&r1_internal_flash_record.ops;
 return r1_stock_registry_register(&r1_internal_flash_record.device);
}
