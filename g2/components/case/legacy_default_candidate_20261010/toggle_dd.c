/* SPDX-License-Identifier: MIT
 * Isolated high opcode 0xdd flag write. The stock path has no length guard.
 */
#include <stdint.h>
uint32_t case_legacy_dd_branch(const uint8_t *command,uint32_t length)
{
    (void)length;
    const uint32_t value=(command[1]!=0u);
    *(volatile uint8_t *)(uintptr_t)0x200000bdu=(uint8_t)value;
    return value;
}
