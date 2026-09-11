/* SPDX-License-Identifier: MIT
 * Board initialization policy: pins 0..12; pin 2 uses function zero,
 * all other entries use function one. Hardware pin roles remain unqualified.
 */
#include <driver/gx_padmux.h>
#define BOARD_DEFAULT(pin) { (pin), ((pin) == 2 ? 0 : 1) }
const GX_PIN_CONFIG open_cfw_gx8002_board_pin_defaults[] = {
    BOARD_DEFAULT(0), BOARD_DEFAULT(1), BOARD_DEFAULT(2),
    BOARD_DEFAULT(3), BOARD_DEFAULT(4), BOARD_DEFAULT(5),
    BOARD_DEFAULT(6), BOARD_DEFAULT(7), BOARD_DEFAULT(8),
    BOARD_DEFAULT(9), BOARD_DEFAULT(10), BOARD_DEFAULT(11), BOARD_DEFAULT(12)
};
_Static_assert(sizeof(GX_PIN_CONFIG) == 2, "Pin table ABI");
_Static_assert(sizeof(open_cfw_gx8002_board_pin_defaults) == 26, "Board pin count");
