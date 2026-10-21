/* SPDX-License-Identifier: MIT. Private event flags create/set/unblock ABI. */
#ifndef OPENCFW_BOOT_EVENT_FLAGS_SET_H
#define OPENCFW_BOOT_EVENT_FLAGS_SET_H
#include <stdint.h>
uintptr_t opencfw_provider_4164da(const uint32_t *attributes);
uint32_t opencfw_provider_41652e(uint32_t *event,uint32_t flags);
uint32_t opencfw_boot_event_flags_set(uint32_t *event,uint32_t flags);
uint32_t opencfw_boot_event_flags_read(uint32_t *event);
void opencfw_boot_event_wait_unblock(uint32_t *item,uint32_t result);
#endif
