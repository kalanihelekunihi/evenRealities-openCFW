/* SPDX-License-Identifier: MIT
 * Native XIP 0x1020681c..0x1020689b. Eight board configuration calls
 * accumulate their real returns; the failure path configures four pins,
 * emits the exact stock diagnostic and spins at the stock terminal branch.
 */
#include <stdint.h>

extern int32_t gx8002_xip_board_pin_configure_102067dc(uint32_t, uint32_t);
extern int32_t gx8002_xip_padmux_set_102065dc(uint32_t, uint32_t);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

void gx8002_xip_board_pin_setup_1020681c(void)
{
    int32_t result = gx8002_xip_board_pin_configure_102067dc(5u, 0u);
    result += gx8002_xip_board_pin_configure_102067dc(6u, 0u);
    result += gx8002_xip_board_pin_configure_102067dc(11u, 0u);
    result += gx8002_xip_board_pin_configure_102067dc(12u, 0u);
    result += gx8002_xip_board_pin_configure_102067dc(7u, 3u);
    result += gx8002_xip_board_pin_configure_102067dc(8u, 3u);
    result += gx8002_xip_board_pin_configure_102067dc(9u, 3u);
    result += gx8002_xip_board_pin_configure_102067dc(10u, 3u);
    if (result == 0) return;
    (void)gx8002_xip_padmux_set_102065dc(5u, 0u);
    (void)gx8002_xip_padmux_set_102065dc(6u, 0u);
    (void)gx8002_xip_padmux_set_102065dc(11u, 0u);
    (void)gx8002_xip_padmux_set_102065dc(12u, 0u);
    (void)gx8002_xip_tws_publish_10206c24(
        "!!!pin set error!\n Please check Board Options!!!");
    for (;;) { }
}
