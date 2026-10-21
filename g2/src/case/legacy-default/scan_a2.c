/* SPDX-License-Identifier: MIT
 * Isolated legacy 0xa2 eight-byte scan and conditional report.
 */
#include <stdint.h>
extern void case_legacy_fill8(uint8_t *out);
extern void case_legacy_hex_log(const uint8_t *bytes, uint32_t count);
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_a2_format[] = "%02x%02x%02x%02x%02x%02x%02x%02x";
static const char case_a2_newline[] = "\r\n";
uint32_t case_legacy_a2_branch(const uint8_t *command, uint32_t length)
{
    (void)command;
    (void)length;
    uint8_t bytes[8];
    case_legacy_fill8(bytes);
    case_legacy_hex_log(bytes, 8u);
    const uint8_t flag = *(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if (flag == 0u)
        return 0u;
    (void)case_legacy_logger(case_a2_format,
        (uint32_t)bytes[0], (uint32_t)bytes[1], (uint32_t)bytes[2],
        (uint32_t)bytes[3], (uint32_t)bytes[4], (uint32_t)bytes[5],
        (uint32_t)bytes[6], (uint32_t)bytes[7]);
    return case_legacy_logger(case_a2_newline);
}
