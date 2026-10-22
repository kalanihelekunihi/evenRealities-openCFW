/* SPDX-License-Identifier: MIT
 * Native CASE 0x08004edc tick accumulation and 0x0800543c clock snapshot,
 * both discovered from direct BL target audit.
 */
#include <stdint.h>
/* Stock 0x08004EDC (case_add_byte0_to_word8) */
void case_boot_clock_accumulate_tick(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x20000118u;
    *(volatile uint32_t *)(uintptr_t)0x20000120u+=state[0u];
}
/* Stock 0x0800543C (case_clock_descriptor) */
void case_boot_clock_snapshot(uint32_t *config,uint32_t *latency)
{
    volatile uint32_t *rcc=(volatile uint32_t *)(uintptr_t)0x40021000u;
    volatile uint32_t *flash=(volatile uint32_t *)(uintptr_t)0x40022000u;
    config[0]=7u;
    config[1]=rcc[2]&7u;
    config[2]=rcc[2]&0xf00u;
    config[3]=rcc[2]&0x7000u;
    *latency=flash[0]&7u;
}
