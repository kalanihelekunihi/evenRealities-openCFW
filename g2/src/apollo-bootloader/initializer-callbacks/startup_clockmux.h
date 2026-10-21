/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_CLOCKMUX_ENTRY_H
#define OPENCFW_CLOCKMUX_ENTRY_H
#include <stdint.h>
/* Input: incoming R1/R2/R5. Output: fields0/1 are live post-body GPIO/pin
 * stack words returned by the original entry in R0/R1. R5 is not overwritten.
 * The assembly entry separately preserves incoming R3 for returned R2.
 */
typedef struct {
    uint32_t r1_carry;
    uint32_t r2_carry;
    uint32_t r5_gpio_carry;
} startup_entry_register_carry_t;
void am_hal_pwrctrl_low_power_init_clockmux_fragment(startup_entry_register_carry_t *entry);
/* opencfw_boot_clockmux_entry is an assembly register-ABI entry, not a C API:
 * caller must provide ambient R1/R2/R3/R5. Use the explicit C function above
 * for ordinary C callers; do not assume a no-argument C call preserves carries.
 */
#endif
