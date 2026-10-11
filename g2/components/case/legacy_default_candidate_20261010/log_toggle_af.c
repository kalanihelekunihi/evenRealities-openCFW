/* SPDX-License-Identifier: MIT
 * Isolated legacy 0xaf log-state toggle; lower formatter is an explicit cut.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_af_hex[] = "%02x";
static const char case_af_newline[] = "\r\n";
uint32_t case_legacy_af_branch(const uint8_t *command, uint32_t length)
{
    volatile uint8_t *const enabled = (volatile uint8_t *)(uintptr_t)0x200000bfu;
    if (length < 2u)
        return *enabled;
    const uint8_t raw = command[1];
    *enabled = (raw != 0u);
    if (raw == 0u)
        return 0u;
    (void)case_legacy_logger(case_af_hex, (uint32_t)raw);
    return case_legacy_logger(case_af_newline);
}
