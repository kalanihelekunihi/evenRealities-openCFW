/* SPDX-License-Identifier: MIT
 * Native CASE 0x08005f44 sensor status flags: OR two live words.
 */
#include <stdint.h>

/* Stock 0x08005F44 (case_or_words_88_8c) */
uint32_t case_boot_sensor_flags_5f44(uint32_t descriptor)
{
    const volatile uint32_t *state=(const volatile uint32_t *)(uintptr_t)descriptor;
    return state[0x88u/4u]|state[0x8cu/4u];
}
