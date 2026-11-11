#ifndef R1_NATIVE_HEALTH_STORAGE_H
#define R1_NATIVE_HEALTH_STORAGE_H
#include <stdint.h>
struct r1_health_pkey_storage { uint8_t initialized,padding[3];uint32_t partition,device; };
extern volatile struct r1_health_pkey_storage r1_health_pkey_storage;
void r1_pkey_fal_bind(void);
uint64_t r1_health_pkey_load_native(void *,uint32_t,uint32_t,uint32_t);
uint64_t r1_health_lifecycle_restore_native(void *,uint32_t,void *,uint32_t);
#endif
