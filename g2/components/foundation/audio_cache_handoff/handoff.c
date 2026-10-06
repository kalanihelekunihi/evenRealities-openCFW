/* SPDX-License-Identifier: MIT */
/* Stock590b6c query and57a7e0 complete getter; separate new checked policy. */
#include "handoff.h"
static uint32_t word(const volatile void *handle, uint32_t offset)
{ return *(const volatile uint32_t *)((const volatile uint8_t *)handle + offset); }
uint32_t opencfw_i2s_selected_buffer(const volatile void *handle, uint32_t selector)
{
    if ((uint8_t)selector == 0u)
        return word(handle, 0x40) == 0xffffffffu ? word(handle, 0x3c) : word(handle, 0x4c);
    return word(handle, 0x48) == 0xffffffffu ? word(handle, 0x44) : word(handle, 0x50);
}
static const volatile void *audio_handle(void)
{ return (const volatile void *)(uintptr_t)*(volatile uint32_t *)(uintptr_t)0x2007450cu; }
uint32_t opencfw_audio_rx_buffer_get(uint32_t *buffer, uint32_t *length)
{
    opencfw_cache_range_t range = { 0, 3200 };
    range.address = opencfw_i2s_selected_buffer(audio_handle(), 0);
    (void)opencfw_cache_invalidate(&range, 0);
    *buffer = range.address;
    *length = range.length;
    return range.address;
}
uint32_t opencfw_cache_checked(const volatile opencfw_cache_range_t *range,
                             uint32_t base, uint32_t capacity, uint32_t operation)
{
    if (!range || !base || !capacity || (base & 31u) || (capacity & 31u) || operation > 2u)
        return 6;
    if (capacity > 0xffffffffu - base) return 6;
    uint32_t length = range->length;
    uint32_t address = range->address;
    if (!length || (length & 0x80000000u) || address < base) return 6;
    uint32_t offset = address - base;
    if (offset >= capacity || length > capacity - offset) return 6;
    /* Bound the32-byte address-block footprint assumed by the stock loop.
     * Physical cache geometry/effects and allocation liveness are unproven.
     * Snapshot prevents later descriptor rereads. */
    opencfw_cache_range_t checked = { address, length };
    return operation == 2u ? opencfw_cache_clean(&checked) :
                            opencfw_cache_invalidate(&checked, operation == 1u);
}
uint32_t opencfw_audio_rx_buffer_get_checked(uint32_t *buffer, uint32_t *length,
                                          uint32_t base, uint32_t capacity)
{
    if (!buffer || !length || buffer == length || !base || !capacity || (base & 31u) || (capacity & 31u) ||
        capacity > 0xffffffffu - base) return 6;
    const volatile void *handle = audio_handle();
    if (!handle) return 6;
    opencfw_cache_range_t range = {
        opencfw_i2s_selected_buffer(handle, 0), 3200
    };
    uint32_t status = opencfw_cache_checked(&range, base, capacity, 0);
    if (status) return status;
    *buffer = range.address;
    *length = range.length;
    return 0;
}
