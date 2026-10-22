/* SPDX-License-Identifier: MIT
 * Complete opcode routing candidate for the fixed CASE command entries.
 * This is an integration source, not an admitted archive provider: the
 * standby chain, flash apply path and physical lower effects remain imports.
 */
#include <stdint.h>
#include <stdbool.h>

extern bool case_legacy_known_dispatch(const uint8_t *, uint32_t, uint32_t *);
extern uint32_t case_legacy_ee_prefix(const uint8_t *, uint32_t);
extern uint32_t case_legacy_ff_prefix(const uint8_t *, uint32_t);
extern bool case_binary_known_dispatch(const uint8_t *, uint32_t, uint32_t,
                                       uint32_t *);
extern uint32_t case_binary_06_41_candidate(const uint8_t *, uint32_t);
/* Stock 0x080068d0. Its transmission and return ABI need lower proof. */
extern void case_binary_ack0641(uint32_t opcode);

/* Stock 0x08000928 (case_legacy_command_candidate) */
uint32_t case_legacy_command_candidate(const uint8_t *command, uint32_t length)
{
    uint32_t result;
    switch (command[0]) {
    case 0xee: return case_legacy_ee_prefix(command, length);
    case 0xff: return case_legacy_ff_prefix(command, length);
    default:
        /* The existing dispatcher covers the remaining 254 byte values. */
        (void)case_legacy_known_dispatch(command, length, &result);
        return result;
    }
}

/* The binary 06/41 source already constructs the stock one-byte handoff. */
uint32_t case_binary_legacy0641(const uint8_t *command, uint32_t length)
{
    return case_legacy_command_candidate(command, length);
}

/* Stock 0x08000E1C (case_binary_command_candidate) */
uint32_t case_binary_command_candidate(const uint8_t *command,
                                        uint32_t length, uint32_t mode)
{
    uint32_t result;
    if (command[2] == 2u &&
        (command[0] == 0x06u || command[0] == 0x41u))
        return case_binary_06_41_candidate(command, length);
    (void)case_binary_known_dispatch(command, length, mode, &result);
    return result;
}
