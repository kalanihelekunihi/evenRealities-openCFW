/* SPDX-License-Identifier: MIT
 * Isolated legacy 0xa4 status-word log with source-owned format text.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_a4_word[] = "%d";
static const char case_a4_newline[] = "\r\n";
uint32_t case_legacy_a4_branch(const uint8_t *command, uint32_t length)
{
    (void)command;(void)length;
    const volatile uint8_t *const flag=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    const volatile uint32_t *const word=(volatile uint32_t *)(uintptr_t)0x20000888u;
    if (*flag==0u) {
        (void)case_legacy_logger(case_a4_word,*word);
        (void)case_legacy_logger(case_a4_newline);
        if (*flag==0u)return 0u;
    }
    (void)case_legacy_logger(case_a4_word,*word);
    return case_legacy_logger(case_a4_newline);
}
