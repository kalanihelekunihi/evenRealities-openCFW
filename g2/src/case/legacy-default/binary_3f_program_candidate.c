/* SPDX-License-Identifier: MIT
 * Isolated stock 0x08009108 retrying output program wrapper.
 * Bus and formatter effects remain lower contracts.
 */
#include <stdint.h>

extern uint32_t case_binary_3f_bus(uint32_t command, uint32_t index,
                                    uint32_t count, const uint8_t *value);
extern uint32_t case_binary_3f_program_log(const char *format, ...);

uint32_t case_binary_3f_program(uint32_t index, uint32_t count,
                                const uint8_t *value)
{
    volatile uint32_t *diagnostics = (volatile uint32_t *)(uintptr_t)0x2000007cu;
    uint32_t result = 0u;
    uint32_t retry = 1u;
    do {
        __asm__ volatile("cpsid i" ::: "memory");
        result = case_binary_3f_bus(0x42u, index, count, value);
        __asm__ volatile("cpsie i" ::: "memory");
        if (result != 0u)
            return result;
        diagnostics[1] += 1u;
        ++retry;
    } while (retry != 10u);

    if (*(volatile uint8_t *)(uintptr_t)0x200000bfu == 0u) {
        case_binary_3f_program_log(
            "write failed--retry number=%d,error_location_2510 is %d,read_bit_2510_error1==%d, read_bit_2510_error2==%d\r\n",
            retry, diagnostics[2], diagnostics[3], diagnostics[4]);
        case_binary_3f_program_log("\r\n");
    }
    return result;
}
