/* SPDX-License-Identifier: MIT
 * Isolated no-action return branch of the fixed CASE legacy command entry.
 * This is intentionally not the public case_legacy_command provider.
 */
#include <stdint.h>
uint32_t case_legacy_default_branch(const uint8_t *command, uint32_t length)
{
    (void)command;
    (void)length;
    return *(volatile uint8_t *)(uintptr_t)0x200000bfu;
}
