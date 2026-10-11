/* SPDX-License-Identifier: MIT
 * Isolated 0xa0 version-report branch with source-owned literal strings.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_a0_version[] = "1.2.57";
static const char case_a0_prefixed[] = "B200 %s, %d";
static const char case_a0_plain[] = "%s, %d";
static const char case_a0_newline[] = "\r\n";
uint32_t case_legacy_a0_branch(const uint8_t *command, uint32_t length)
{
    (void)command;
    (void)length;
    const volatile uint8_t *const flag = (volatile uint8_t *)(uintptr_t)0x200000bfu;
    const volatile uint32_t *const counter = (volatile uint32_t *)(uintptr_t)0x20000884u;
    if (*flag == 0u) {
        (void)case_legacy_logger(case_a0_prefixed, case_a0_version, *counter);
        (void)case_legacy_logger(case_a0_newline);
        if (*flag == 0u)
            return 0u;
    }
    (void)case_legacy_logger(case_a0_plain, case_a0_version, *counter);
    return case_legacy_logger(case_a0_newline);
}
