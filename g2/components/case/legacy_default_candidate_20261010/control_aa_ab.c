/* SPDX-License-Identifier: MIT
 * Isolated legacy 0xaa and 0xab lower-call dispatch branches.
 */
#include <stdint.h>
extern uint32_t case_legacy_aa_first(uint32_t prior);
extern uint32_t case_legacy_aa_second(uint32_t prior);
extern uint32_t case_legacy_ab_child(uint32_t prior);
uint32_t case_legacy_aa_branch(const uint8_t *command, uint32_t length)
{
    (void)command;(void)length;
    const uint32_t prior=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    return case_legacy_aa_second(case_legacy_aa_first(prior));
}
uint32_t case_legacy_ab_branch(const uint8_t *command, uint32_t length)
{
    (void)command;(void)length;
    const uint32_t prior=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    return case_legacy_ab_child(prior);
}
