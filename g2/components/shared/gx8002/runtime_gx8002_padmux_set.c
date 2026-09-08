/* SPDX-License-Identifier: MIT
 * Recovered from G2 codec 2.2.6.10, package 0xfb68.
 * Preserve write-before-check behavior even for invalid function arguments.
 */
#include <stdint.h>
extern int open_cfw_gx8002_padmux_check(int pad_id, int function);
int open_cfw_gx8002_padmux_set(int pad_id, int function)
{
    unsigned int pin = (unsigned int)pad_id;
    if (pin > 32u)
        return -1;
    volatile uint32_t *word = (volatile uint32_t *)(uintptr_t)
        (0xa0010090u + (pin / 8u) * 4u);
    unsigned int shift = (pin % 8u) * 4u;
    uint32_t previous = *word;
    *word = (previous & ~(15u << shift)) |
            (((unsigned int)function & 15u) << shift);
    return open_cfw_gx8002_padmux_check(pad_id, function) == 0 ? 0 : -1;
}
