/* SPDX-License-Identifier: MIT
 * Isolated destination-2 binary 0x06/0x41 acknowledgement and legacy handoff.
 */
#include <stdint.h>
extern void case_binary_ack0641(uint32_t opcode);
extern uint32_t case_binary_legacy0641(const uint8_t *command, uint32_t length);
uint32_t case_binary_06_41_candidate(const uint8_t *command, uint32_t logical_length)
{
    (void)logical_length;
    uint8_t next = command[0] == 0x06u ? 0xeeu : 0xffu;
    case_binary_ack0641(command[0]);
    return case_binary_legacy0641(&next, 1);
}
