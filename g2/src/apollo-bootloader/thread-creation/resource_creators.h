/* SPDX-License-Identifier: MIT. Private ARM32 bootloader object constructors. */
#ifndef OPENCFW_BOOT_RESOURCE_CREATORS_H
#define OPENCFW_BOOT_RESOURCE_CREATORS_H
#include <stdint.h>
uintptr_t opencfw_provider_4163b2(uintptr_t callback,uint32_t type,
    uintptr_t argument,const uint32_t *attributes);
uintptr_t opencfw_provider_416610(const uint32_t *attributes);
uintptr_t opencfw_boot_timer_id_get(uint32_t *timer);
void opencfw_boot_timer_callback_dispatcher(uint32_t *timer);
void opencfw_boot_timer_object_initialize(uintptr_t name,uint32_t period,
    uint32_t periodic,uintptr_t id,uintptr_t callback,uint32_t *timer);
uintptr_t opencfw_boot_timer_create_dynamic(uintptr_t name,uint32_t period,
    uint32_t periodic,uintptr_t id,uintptr_t callback);
uintptr_t opencfw_boot_timer_create_static(uintptr_t name,uint32_t period,
    uint32_t periodic,uintptr_t id,uintptr_t callback,uint32_t *timer);
void opencfw_boot_mutex_object_initialize(uint32_t *queue);
uintptr_t opencfw_boot_mutex_create_dynamic(uint32_t type);
uintptr_t opencfw_boot_mutex_create_static(uint32_t type,uint32_t *storage);
#endif
