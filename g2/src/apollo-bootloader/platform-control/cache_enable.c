/* SPDX-License-Identifier: MIT
 * Reconstructed locked bootloader 41e1e8 / 41e266. SCB operations retain
 * original order; offline register tests do not establish cache coherence.
 */
#include "cache_enable.h"
#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
static void dsb(void) { __asm__ volatile("dsb sy" ::: "memory"); }
static void isb(void) { __asm__ volatile("isb sy" ::: "memory"); }
uint32_t opencfw_boot_icache_enable(void) {
    if (REG(0xe001e300u) & 0x300u) return 1u;
    if (!(REG(0xe000ed14u) & 0x20000u)) {
        dsb(); isb(); REG(0xe000ef50u)=0u; dsb(); isb();
        REG(0xe000ed14u) |= 0x20000u; dsb(); isb();
    }
    return 0u;
}
static void invalidate_sets(uint32_t destination) {
    uint32_t descriptor=REG(0xe000ed80u);
    uint32_t set=(descriptor>>13)&0x7fffu;
    for (;;) {
        uint32_t way=(descriptor>>3)&0x3ffu;
        for (;;) {
            REG(destination)=((set<<5)&0x3fe0u)|(way<<30);
            if (!way) break;
            --way;
        }
        if (!set) break;
        --set;
    }
}
uint32_t opencfw_boot_dcache_enable(uint32_t clean_after) {
    if (REG(0xe001e300u)&0x300u) return 1u;
    volatile const uint8_t *configuration=(const uint8_t *)0x20000078u;
    REG(0xe001e004u)=((configuration[0]<<7)&0x380u)
        |((configuration[1]<<4)&0x70u)|((configuration[2]<<1)&0xeu)|1u;
    if (!(REG(0xe000ed14u)&0x10000u)) {
        REG(0xe000ed84u)=0u; dsb(); invalidate_sets(0xe000ef60u);
        dsb(); REG(0xe000ed14u)|=0x10000u; dsb(); isb();
    }
    if ((uint8_t)clean_after) {
        REG(0xe000ed84u)=0u; dsb(); invalidate_sets(0xe000ef6cu);
        dsb(); isb();
    }
    return 0u;
}
