/* SPDX-License-Identifier: MIT
 * Initial policy flags independently located at native RAM consumers.
 * 0x200000be gates periodic watchdog feed (policy idle/command 0xdf).
 * 0x20000104 is a one-byte IRQ latch written by native vector 0x3c2c.
 * 0x20000105 gates charging/service work (0xd2/0xd3 and app policy).
 */
#include <stdint.h>

void case_crt_init_policy_flags(void)
{
    *(volatile uint8_t *)(uintptr_t)0x200000beu=1u;
    *(volatile uint8_t *)(uintptr_t)0x20000104u=1u;
    *(volatile uint8_t *)(uintptr_t)0x20000105u=1u;
}
