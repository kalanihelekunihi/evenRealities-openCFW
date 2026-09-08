/* SPDX-License-Identifier: MIT
 * Default mux policy: initialize pins 0..31 to function zero.
 * Pin 32 is accepted by individual accessors but absent from this boot table.
 */
#include <driver/gx_padmux.h>
#define DEFAULT_PIN(pin) { (pin), 0 }
const GX_PIN_CONFIG open_cfw_gx8002_padmux_defaults[32] = {
    DEFAULT_PIN(0), DEFAULT_PIN(1), DEFAULT_PIN(2), DEFAULT_PIN(3), DEFAULT_PIN(4), DEFAULT_PIN(5), DEFAULT_PIN(6), DEFAULT_PIN(7),
    DEFAULT_PIN(8), DEFAULT_PIN(9), DEFAULT_PIN(10), DEFAULT_PIN(11), DEFAULT_PIN(12), DEFAULT_PIN(13), DEFAULT_PIN(14), DEFAULT_PIN(15),
    DEFAULT_PIN(16), DEFAULT_PIN(17), DEFAULT_PIN(18), DEFAULT_PIN(19), DEFAULT_PIN(20), DEFAULT_PIN(21), DEFAULT_PIN(22), DEFAULT_PIN(23),
    DEFAULT_PIN(24), DEFAULT_PIN(25), DEFAULT_PIN(26), DEFAULT_PIN(27), DEFAULT_PIN(28), DEFAULT_PIN(29), DEFAULT_PIN(30), DEFAULT_PIN(31),
};
#undef DEFAULT_PIN
_Static_assert(sizeof(open_cfw_gx8002_padmux_defaults) == 64,
               "Padmux default table layout");
