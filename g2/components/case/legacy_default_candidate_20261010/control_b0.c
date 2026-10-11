/* SPDX-License-Identifier: MIT
 * Isolated high opcode 0xb0 lower command, stock R0/R1 contract.
 */
#include <stdint.h>
extern uint32_t case_legacy_b0_child(uint32_t handle,uint32_t span);
uint32_t case_legacy_b0_branch(const uint8_t *command,uint32_t length)
{
    (void)command;(void)length;
    const uint32_t handle=*(volatile uint32_t *)(uintptr_t)0x200000f0u;
    return case_legacy_b0_child(handle,256u);
}
