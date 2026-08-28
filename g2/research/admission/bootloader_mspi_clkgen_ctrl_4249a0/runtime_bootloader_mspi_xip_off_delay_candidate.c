/* SPDX-License-Identifier: BSD-3-Clause */
#include <stdint.h>
#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline)) void open_cfw_bootloader_mspi_xip_off_delay_424a18(void) { __asm__ volatile(
"ldrb r1, [r0, #0xc]\nsubs r1, r1, #6\ncmp r1, #3\nbls 4f\nsubs r1, r1, #4\ncmp r1, #3\nbls 3f\nsubs r1, r1, #4\ncmp r1, #1\nbls 2f\nsubs r1, r1, #4\ncmp r1, #1\nbls 2f\nsubs r1, r1, #2\ncmp r1, #3\nbhi 5f\nmovs r1, #1\nstr.w r1, [r0, #0x8cc]\nb 5f\n2:\nmovs r1, #2\nstr.w r1, [r0, #0x8cc]\nb 5f\n3:\nmovs r1, #4\nstr.w r1, [r0, #0x8cc]\nb 5f\n4:\nmovs r1, #8\nstr.w r1, [r0, #0x8cc]\nb 5f\n5:\nbx lr\n"); }
#else
uint32_t open_cfw_bootloader_mspi_xip_off_delay_424a18(uint8_t clock_frequency,
                                                       uint32_t current)
{
    if (clock_frequency >= 6U && clock_frequency <= 9U) return 8U;
    if (clock_frequency >= 10U && clock_frequency <= 13U) return 4U;
    if ((clock_frequency >= 14U && clock_frequency <= 15U) ||
        (clock_frequency >= 18U && clock_frequency <= 19U)) return 2U;
    if (clock_frequency >= 20U && clock_frequency <= 23U) return 1U;
    return current;
}
#endif
