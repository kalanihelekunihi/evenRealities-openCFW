/* SPDX-License-Identifier: MIT
 * Experimental wiring for the existing CASE frame dispatcher. The dispatcher
 * calls these as void functions and ignores the original register result.
 * Do not select this object for a device image until lower contracts close.
 */
#include <stdint.h>

extern uint32_t case_legacy_command_candidate(const uint8_t *,uint32_t);
extern uint32_t case_binary_command_candidate(const uint8_t *,uint32_t,uint32_t);

void case_legacy_command(uint8_t *command,uint16_t length)
{
    (void)case_legacy_command_candidate(command,length);
}
void case_binary_command(uint8_t *command,uint16_t length,uint32_t mode)
{
    (void)case_binary_command_candidate(command,length,mode);
}
