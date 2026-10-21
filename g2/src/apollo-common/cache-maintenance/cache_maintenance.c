/* SPDX-License-Identifier: MIT */
/* Reconstructed stock475014/47510e register/barrier contract; not SDK source. */
#include "cache_maintenance.h"
static volatile uint32_t *reg(uint32_t address)
{ return (volatile uint32_t *)(uintptr_t)address; }
static void dsb(void) { __asm__ volatile("dsb sy" ::: "memory"); }
static void isb(void) { __asm__ volatile("isb sy" ::: "memory"); }
static uint32_t positive_signed32(uint32_t value)
{ return value != 0u && (value & 0x80000000u) == 0u; }
static void whole(uint32_t operation)
{
    *reg(0xe000ed84u) = 0; /* CSSELR */
    dsb();
    uint32_t size = *reg(0xe000ed80u); /* CCSIDR */
    uint32_t sets = (size >> 13) & 0x7fffu;
    uint32_t ways = (size >> 3) & 0x3ffu;
    do {
        uint32_t way = ways;
        do {
            *reg(operation) = ((sets << 5) & 0x3fe0u) | (way << 30);
        } while (way-- != 0u);
    } while (sets-- != 0u);
    dsb();
    isb();
}
static void range_operation(const volatile opencfw_cache_range_t *range, uint32_t operation)
{
    /* Preserve stock length-before-address loads even on nonpositive length. */
    uint32_t remaining = range->length;
    uint32_t address = range->address;
    if (!positive_signed32(remaining)) return;
    remaining += address & 31u;
    dsb();
    do {
        *reg(operation) = address;
        address += 32u;
        remaining -= 32u;
    } while (positive_signed32(remaining));
    dsb();
    isb();
}
uint32_t opencfw_cache_invalidate(const volatile opencfw_cache_range_t *range, uint32_t clean_too)
{
    if ((*reg(0xe000ed14u) & 0x10000u) == 0u) {
        dsb(); isb(); return 0;
    }
    if (!range) whole((uint8_t)clean_too ? 0xe000ef74u : 0xe000ef60u);
    else range_operation(range, (uint8_t)clean_too ? 0xe000ef70u : 0xe000ef5cu);
    return 0;
}
uint32_t opencfw_cache_clean(const volatile opencfw_cache_range_t *range)
{
    if ((*reg(0xe000ed14u) & 0x10000u) == 0u) {
        dsb(); isb(); return 0;
    }
    if (!range) whole(0xe000ef6cu);
    else range_operation(range, 0xe000ef68u);
    return 0;
}
