/* SPDX-License-Identifier: MIT
 * Isolated 0xae state/log branch; logger remains an explicit lower cut.
 */
#include <stdint.h>
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_ae_message[] = "%s reset GLS";
static const char case_ae_enable[] = "Enable";
static const char case_ae_disable[] = "Disable";
static const char case_ae_newline[] = "\r\n";
uint32_t case_legacy_ae_branch(const uint8_t *command, uint32_t length)
{
    const uint8_t log_flag = *(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if (length < 2u)
        return log_flag;
    const uint8_t value = (command[1] != 0u);
    *(volatile uint8_t *)(uintptr_t)0x200000c0u = value;
    if (log_flag != 0u)
        return log_flag;
    (void)case_legacy_logger(case_ae_message,
                             value ? case_ae_disable : case_ae_enable);
    return case_legacy_logger(case_ae_newline);
}
