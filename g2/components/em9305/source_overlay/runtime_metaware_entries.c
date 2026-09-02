/* SPDX-License-Identifier: MIT */

#include "runtime_metaware.h"

#define OPEN_CFW_EM9305_META_ENTRY(name) \
    __attribute__((used, noinline, aligned(2), section(".text.meta.entry." name)))

OPEN_CFW_EM9305_META_ENTRY("302664")
void *open_cfw_em9305_entry_memmove_302664(
    void *destination, const void *source, size_t length
)
{
    return open_cfw_em9305_metaware_memmove(destination, source, length);
}

OPEN_CFW_EM9305_META_ENTRY("302748")
uint64_t open_cfw_em9305_entry_udiv64_302748(
    uint64_t dividend, uint64_t divisor
)
{
    return open_cfw_em9305_metaware_udiv64(dividend, divisor);
}

OPEN_CFW_EM9305_META_ENTRY("302760")
int64_t open_cfw_em9305_entry_sdiv64_302760(
    int64_t dividend, int64_t divisor
)
{
    return open_cfw_em9305_metaware_sdiv64(dividend, divisor);
}

OPEN_CFW_EM9305_META_ENTRY("3027c8")
uint64_t open_cfw_em9305_entry_shift_left64_3027c8(
    uint64_t value, uint32_t count
)
{
    return open_cfw_em9305_metaware_shift_left64(value, count);
}

OPEN_CFW_EM9305_META_ENTRY("3027f4")
uint64_t open_cfw_em9305_entry_shift_right64_3027f4(
    uint64_t value, uint32_t count
)
{
    return open_cfw_em9305_metaware_shift_right64(value, count);
}

OPEN_CFW_EM9305_META_ENTRY("302820")
void open_cfw_em9305_entry_stack_guard_302820(void)
{
    open_cfw_em9305_metaware_stack_guard();
}

OPEN_CFW_EM9305_META_ENTRY("332fc4")
void *open_cfw_em9305_entry_memcpy_332fc4(
    void *destination, const void *source, size_t length
)
{
    return open_cfw_em9305_metaware_memcpy(destination, source, length);
}

OPEN_CFW_EM9305_META_ENTRY("33301c")
void *open_cfw_em9305_entry_memset_33301c(
    void *destination, int value, size_t length
)
{
    return open_cfw_em9305_metaware_memset(destination, value, length);
}
