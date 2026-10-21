/* SPDX-License-Identifier: MIT
 * Legacy command lowers with the same original entry addresses as independently
 * compared binary-command children. Their physical flash/sensor reads remain
 * runtime contracts; no stock flash data is embedded here.
 */
#include <stdint.h>

extern uint8_t *case_binary_fill51(uint8_t *out);      /* 0x08002f60 */
extern uint32_t case_binary_14_read_a(uint32_t *out); /* 0x08009ff0 */
extern uint32_t case_binary_14_read_b(uint32_t *out); /* 0x08009f18 */
extern uint32_t case_binary_14_read_c(uint32_t *out); /* 0x0800a01e */

void case_legacy_fill8(uint8_t *out)
{
    (void)case_binary_fill51(out);
}
uint32_t case_legacy_value_a(uint32_t *out)
{
    return case_binary_14_read_a(out);
}
uint32_t case_legacy_value_b(uint32_t *out)
{
    return case_binary_14_read_b(out);
}
uint32_t case_legacy_value_c(uint32_t *out)
{
    return case_binary_14_read_c(out);
}
