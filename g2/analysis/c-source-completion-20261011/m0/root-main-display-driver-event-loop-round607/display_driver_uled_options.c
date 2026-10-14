/* S200 uLED option records at 0x70afe4 and 0x70b024.
 * These are exact decoded flash records. Function-address relocation remains
 * an open whole-image gate; the values below name native entry addresses.
 */
#include <stdint.h>

const uint32_t display_driver_uled_option_type1[16] = {
    0x005bbd49u, 0x005bc76fu, 0x005bbd71u, 0x005bbda5u,
    0x005bcb6du, 0x005bcbb5u, 0x005bc6afu, 0x005bcb29u,
    0x005bcc11u, 0x005bc4c1u, 0x005bcd45u, 0x005bcc19u,
    0x005bd015u, 0x005bd39du, 0x005bc8b5u, 0x00000001u
};

const uint32_t display_driver_uled_option_type0[16] = {
    0x00592659u, 0x00592f9bu, 0x00592681u, 0x005926b5u,
    0x00593201u, 0x0059328du, 0x00592e9du, 0x005931c1u,
    0x00593335u, 0x00592aa9u, 0x00592debu, 0x00592cb5u,
    0x005936a5u, 0x00593751u, 0x00000000u, 0x00000000u
};

_Static_assert(sizeof display_driver_uled_option_type1 == 64u, "uLED option size");
_Static_assert(sizeof display_driver_uled_option_type0 == 64u, "uLED option size");
