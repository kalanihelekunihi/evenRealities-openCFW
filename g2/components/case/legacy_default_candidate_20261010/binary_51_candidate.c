/* SPDX-License-Identifier: MIT
 * Isolated stock opcode 0x51, destination-2 branch.
 */
#include <stdint.h>
extern uint8_t *case_binary_fill51(uint8_t *payload_tail);
extern uint32_t case_binary_send51(const uint8_t *payload, uint32_t length);
uint32_t case_binary_51_candidate(const uint8_t *command, uint32_t logical_length)
{
    (void)command;
    (void)logical_length;
    uint8_t reply[12] = {0x51,0x01,0x03,0x08,0,0,0,0,0,0,0,0};
    (void)case_binary_fill51(reply+4);
    return case_binary_send51(reply, 12);
}
