/* SPDX-License-Identifier: MIT
 * Reconstructed board pin guard at package 0xfd68 / runtime 0x102067dc.
 * Candidate only: decoded/helper composition qualification remains required.
 */
#include <stdint.h>
extern int open_cfw_gx8002_padmux_check(int pin, int function);
extern int open_cfw_gx8002_padmux_set(int pin, int function);
extern int open_cfw_gx8002_printf(const char *format, ...);

int open_cfw_gx8002_board_pin_configure(int pin, int function)
{
    volatile uint32_t *initialized = (volatile uint32_t *)(uintptr_t)0x20027b4cu;
    if (!*initialized && open_cfw_gx8002_padmux_check(pin, pin != 2)) {
        open_cfw_gx8002_printf((const char *)(uintptr_t)0x1020ad4au, pin);
        return -1;
    }
    (void)open_cfw_gx8002_padmux_set(pin, function);
    return 0;
}
