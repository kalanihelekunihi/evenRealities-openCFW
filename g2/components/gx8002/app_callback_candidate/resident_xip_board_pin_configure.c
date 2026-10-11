/* SPDX-License-Identifier: MIT
 * Native XIP 0x102067dc..0x10206813 and exact stock conflict string.
 */
#include <stdint.h>

extern int32_t gx8002_xip_padmux_check_102065b8(uint32_t, uint32_t);
extern int32_t gx8002_xip_padmux_set_102065dc(uint32_t, uint32_t);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

int32_t gx8002_xip_board_pin_configure_102067dc(uint32_t pin,
                                                   uint32_t function)
{
    volatile const uint32_t *const initialized =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20027b4c);
    if (*initialized == 0u &&
        gx8002_xip_padmux_check_102065b8(pin, pin != 2u) != 0) {
        (void)gx8002_xip_tws_publish_10206c24(
            "pin %d function conflict !\n", pin);
        return -1;
    }
    (void)gx8002_xip_padmux_set_102065dc(pin, function);
    return 0;
}
