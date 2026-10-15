/* Partial source-owned S200 uLED option records. Entries 0 are linked C
 * callbacks; the remaining 27 callback entries retain authenticated native
 * Thumb addresses. This is a trial relocation, not a complete option table.
 */
#include <stdint.h>
extern void display_driver_uled_option_type0_irq_592658(void);
extern void display_driver_uled_option_type1_irq_5bbd48(void);

const uintptr_t display_driver_uled_option_type1[16] = {
    (uintptr_t)&display_driver_uled_option_type1_irq_5bbd48,
    0x005bc76fu, 0x005bbd71u, 0x005bbda5u,
    0x005bcb6du, 0x005bcbb5u, 0x005bc6afu, 0x005bcb29u,
    0x005bcc11u, 0x005bc4c1u, 0x005bcd45u, 0x005bcc19u,
    0x005bd015u, 0x005bd39du, 0x005bc8b5u, 0x00000001u
};

const uintptr_t display_driver_uled_option_type0[16] = {
    (uintptr_t)&display_driver_uled_option_type0_irq_592658,
    0x00592f9bu, 0x00592681u, 0x005926b5u,
    0x00593201u, 0x0059328du, 0x00592e9du, 0x005931c1u,
    0x00593335u, 0x00592aa9u, 0x00592debu, 0x00592cb5u,
    0x005936a5u, 0x00593751u, 0x00000000u, 0x00000000u
};

_Static_assert(sizeof display_driver_uled_option_type1 == 64u, "uLED option size");
_Static_assert(sizeof display_driver_uled_option_type0 == 64u, "uLED option size");
