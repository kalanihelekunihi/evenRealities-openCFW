/* SPDX-License-Identifier: MIT
 * Isolated 0xa1 legacy command branch; lower GPIO calls remain explicit.
 */
#include <stdint.h>
extern void case_legacy_gpio_bit4(uint32_t value);
extern uint32_t case_legacy_gpio_bit0(uint32_t value);
uint32_t case_legacy_a1_branch(const uint8_t *command, uint32_t length)
{
    if (length < 2u)
        return *(volatile uint8_t *)(uintptr_t)0x200000bfu;
    (void)case_legacy_gpio_bit4(command[1] & 0x10u);
    return case_legacy_gpio_bit0(command[1] & 1u);
}
