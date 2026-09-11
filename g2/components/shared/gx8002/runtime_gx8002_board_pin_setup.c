/* SPDX-License-Identifier: MIT
 * Recovered eight-pin board setup and its original fatal-error path.
 */
#include <stdint.h>
extern int open_cfw_gx8002_board_pin_configure(int pin, int function);
extern int open_cfw_gx8002_padmux_set(int pin, int function);
extern int open_cfw_gx8002_printf(const char *format, ...);

void open_cfw_gx8002_board_pin_setup(void)
{
    unsigned int errors = (unsigned int)open_cfw_gx8002_board_pin_configure(5, 0);
    errors += (unsigned int)open_cfw_gx8002_board_pin_configure(6, 0);
    errors += (unsigned int)open_cfw_gx8002_board_pin_configure(11, 0);
    errors += (unsigned int)open_cfw_gx8002_board_pin_configure(12, 0);
    errors += (unsigned int)open_cfw_gx8002_board_pin_configure(7, 3);
    errors += (unsigned int)open_cfw_gx8002_board_pin_configure(8, 3);
    errors += (unsigned int)open_cfw_gx8002_board_pin_configure(9, 3);
    errors += (unsigned int)open_cfw_gx8002_board_pin_configure(10, 3);
    if (errors) {
        (void)open_cfw_gx8002_padmux_set(5, 0);
        (void)open_cfw_gx8002_padmux_set(6, 0);
        (void)open_cfw_gx8002_padmux_set(11, 0);
        (void)open_cfw_gx8002_padmux_set(12, 0);
        open_cfw_gx8002_printf((const char *)(uintptr_t)0x1020ad66u);
        for (;;) { }
    }
}
