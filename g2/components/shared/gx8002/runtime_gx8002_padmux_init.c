/* SPDX-License-Identifier: MIT
 * Recovered G2 codec initializer, package 0xfbbc.
 */
#include <driver/gx_padmux.h>
extern const GX_PIN_CONFIG open_cfw_gx8002_padmux_defaults[32];
extern int open_cfw_gx8002_padmux_set(int pin, int function);
int open_cfw_gx8002_padmux_init(const GX_PIN_CONFIG *table, int size)
{
    if (!table || size < 0)
        return -1;
    const GX_PIN_CONFIG *end = table + size;
    for (unsigned int i = 0; i < 32; ++i) {
        int pin = open_cfw_gx8002_padmux_defaults[i].pin_id;
        const GX_PIN_CONFIG *entry = table;
        while (entry != end && entry->pin_id != pin)
            ++entry;
        int function = entry == end ?
            open_cfw_gx8002_padmux_defaults[i].function : entry->function;
        (void)open_cfw_gx8002_padmux_set(pin, function);
    }
    return 0;
}
