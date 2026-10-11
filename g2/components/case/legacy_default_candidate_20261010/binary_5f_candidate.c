/* SPDX-License-Identifier: MIT
 * Isolated stock opcode 0x5f, destination-2 branch.
 */
#include <stdint.h>
extern uint8_t *case_binary_fill5f(uint8_t *payload_tail);
extern uint32_t case_binary_send5f(const uint8_t *payload, uint32_t length);
uint32_t case_binary_5f_candidate(const uint8_t *command, uint32_t logical_length)
{
    (void)command;
    (void)logical_length;
    uint8_t reply[20] = {0x5f,0x01,0x03,0x10};
    (void)case_binary_fill5f(reply+4);
    return case_binary_send5f(reply, 20);
}
