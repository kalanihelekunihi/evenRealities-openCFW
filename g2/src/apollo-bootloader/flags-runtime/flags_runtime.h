/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_FLAGS_RUNTIME_H
#define OPENCFW_BOOTLOADER_FLAGS_RUNTIME_H

#include <stdint.h>

void opencfw_provider_41866a(uint32_t *waiter_count, uint32_t wait_flags,
                             uint32_t timeout_ticks);
uint32_t opencfw_provider_416590(uint32_t *event_flags, uint32_t mask,
                                 uint32_t options, uint32_t timeout_ticks);
uint32_t opencfw_provider_4199dc(uint32_t *event_flags, uint32_t mask,
                                 uint32_t clear_on_exit, uint32_t wait_all,
                                 uint32_t timeout_ticks);
uint32_t opencfw_provider_418d7a(void);
uint32_t opencfw_provider_41623a(uint32_t *thread, int32_t flags);
uint64_t opencfw_provider_4162c4(uint32_t mask, uint32_t options,
                                  uint32_t timeout_ticks, uint32_t opaque);

#endif
