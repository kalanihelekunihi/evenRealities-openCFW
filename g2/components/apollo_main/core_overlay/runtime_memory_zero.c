/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacement for the G2 2.2.6.10 runtime zero-fill adapter
 * at 0x004826FC...0x00482707. The stock adapter forwards
 * (destination, 0, size) to the shared byte-fill primitive and preserves its
 * destination return value. The replacement reuses the source-owned LVGL
 * zeroing primitive while preserving that return ABI.
 */

#ifndef OPEN_CFW_RUNTIME_MEMORY_ZERO_FILL
void open_cfw_lv_memory_zero(void *destination, unsigned int size);
#define OPEN_CFW_RUNTIME_MEMORY_ZERO_FILL(destination, size) \
    open_cfw_lv_memory_zero((destination), (size))
#endif

__attribute__((used, noinline))
void *open_cfw_runtime_memory_zero(void *destination, unsigned int size)
{
    OPEN_CFW_RUNTIME_MEMORY_ZERO_FILL(destination, size);
    return destination;
}

#undef OPEN_CFW_RUNTIME_MEMORY_ZERO_FILL
