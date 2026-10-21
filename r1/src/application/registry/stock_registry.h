#ifndef R1_STOCK_REGISTRY_H
#define R1_STOCK_REGISTRY_H
#include "generic_device_registry/generic_device_registry.h"
/* Native stock ABI: one name or record argument, fixed list-head storage. */
extern generic_device_registry_device *r1_stock_registry_head;
generic_device_registry_device *r1_stock_registry_find(const char *name);
uint32_t r1_stock_registry_register(generic_device_registry_device *record);
/* Slot 00/08/0c take the device only; 18/20 take two extra words. */
uint32_t r1_stock_dispatch_00(generic_device_registry_device *device);
uint32_t r1_stock_dispatch_08(generic_device_registry_device *device);
uint32_t r1_stock_dispatch_0c(generic_device_registry_device *device);
uint32_t r1_stock_dispatch_18(generic_device_registry_device *device, uintptr_t a, uintptr_t b);
uint32_t r1_stock_dispatch_20(generic_device_registry_device *device, uintptr_t a, uintptr_t b);
uint32_t r1_stock_dispatch_10(generic_device_registry_device *device, uintptr_t a, uintptr_t b, uintptr_t c);
uint32_t r1_stock_dispatch_14(generic_device_registry_device *device, uintptr_t a, uintptr_t b, uintptr_t c);
#endif
