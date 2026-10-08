/* SPDX-License-Identifier: MIT
 * Source reconstruction of stock helper 0x41d294 (mode-1 device snapshot).
 * Peripheral and core-debug reads are volatile and preserve stock order.
 */
#include "device_info.h"

#define SYS_STATUS ((volatile uint32_t *)(uintptr_t)0x40020000u)
#define DEBUG0 (*(volatile uint32_t *)(uintptr_t)0xe00fefe0u)
#define DEBUG1 (*(volatile uint32_t *)(uintptr_t)0xe00fefe4u)
#define DEBUG2 (*(volatile uint32_t *)(uintptr_t)0xe00fefe8u)
#define DEBUG3 (*(volatile uint32_t *)(uintptr_t)0xe00fefecu)
#define DEBUG4 (*(volatile uint32_t *)(uintptr_t)0xe00feffcu)
#define DEBUG5 (*(volatile uint32_t *)(uintptr_t)0xe00feff8u)
#define DEBUG6 (*(volatile uint32_t *)(uintptr_t)0xe00feff4u)
#define DEBUG7 (*(volatile uint32_t *)(uintptr_t)0xe00feff0u)

extern void opencfw_hal_delay_us(uint32_t microseconds);
extern const uint16_t opencfw_boot_storage_range_limits[4];

__attribute__((section(".boot_device_clock_factors"), used))
const uint16_t opencfw_boot_device_clock_factors[12] = {
    0x0080u, 0x0100u, 0x0400u, 0x0080u, 0x0100u, 0x0800u,
    0x0100u, 0x0200u, 0x0800u, 0x0100u, 0x0200u, 0x0c00u,
};

void opencfw_boot_device_info_initialize(volatile uint32_t *record)
{
    record[0] = SYS_STATUS[0];
    record[1] = SYS_STATUS[1];
    record[2] = SYS_STATUS[2];
    record[3] = SYS_STATUS[3];
    record[4] = SYS_STATUS[4];
    record[5] = SYS_STATUS[5];
    record[6] = 1u;
    record[11] = (uint32_t)opencfw_boot_storage_range_limits[
        (SYS_STATUS[5] >> 2) & 3u] << 10;
    record[8] = (uint32_t)opencfw_boot_device_clock_factors[
        (SYS_STATUS[5] & 3u) * 3u] << 10;
    record[9] = (uint32_t)opencfw_boot_device_clock_factors[
        (SYS_STATUS[5] & 3u) * 3u + 1u] << 10;
    record[10] = (uint32_t)opencfw_boot_device_clock_factors[
        (SYS_STATUS[5] & 3u) * 3u + 2u] << 10;

    record[12] = DEBUG0 & 0xffu;
    opencfw_hal_delay_us(10u);
    record[12] |= (DEBUG1 & 0x0fu) << 8;
    opencfw_hal_delay_us(10u);
    record[13] = (DEBUG1 >> 4) & 0x0fu;
    opencfw_hal_delay_us(10u);
    record[13] |= (DEBUG2 & 0x0fu) << 4;
    opencfw_hal_delay_us(10u);
    record[14] = ((DEBUG2 >> 4) & 0x0fu) << 4;
    opencfw_hal_delay_us(10u);
    record[14] |= (DEBUG3 >> 4) & 0x0fu;
    opencfw_hal_delay_us(10u);
    record[15] = DEBUG4 << 24;
    opencfw_hal_delay_us(10u);
    record[15] |= (DEBUG5 & 0xffu) << 16;
    opencfw_hal_delay_us(10u);
    record[15] |= (DEBUG6 & 0xffu) << 8;
    opencfw_hal_delay_us(10u);
    record[15] |= DEBUG7 & 0xffu;
    opencfw_hal_delay_us(10u);
}
