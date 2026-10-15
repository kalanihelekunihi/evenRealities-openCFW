/* Partial source-owned S200 uLED option records. Eight callbacks use C symbols;
 * the other 21 distinct callback addresses remain authenticated native values.
 */
#include <stdint.h>
extern void display_driver_uled_option_type0_irq_592658(void);
extern void display_driver_uled_option_type1_irq_5bbd48(void);
extern uint32_t display_driver_uled_option_type1_mask_5bcc10(uint32_t);
extern uint32_t display_driver_uled_option_type1_noop_5bd39c(void);
extern uint32_t display_driver_uled_option_type0_setup_592680(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_option_type1_setup_5bbd70(uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_option_type0_enable_5926b4(uint32_t);
extern uint32_t display_driver_uled_option_type1_enable_5bbda4(uint32_t);

const uintptr_t display_driver_uled_option_type1[16] = {
    (uintptr_t)&display_driver_uled_option_type1_irq_5bbd48,
    0x005bc76fu,
    (uintptr_t)&display_driver_uled_option_type1_setup_5bbd70,
    (uintptr_t)&display_driver_uled_option_type1_enable_5bbda4,
    0x005bcb6du, 0x005bcbb5u, 0x005bc6afu, 0x005bcb29u,
    (uintptr_t)&display_driver_uled_option_type1_mask_5bcc10,
    0x005bc4c1u, 0x005bcd45u, 0x005bcc19u,
    0x005bd015u,
    (uintptr_t)&display_driver_uled_option_type1_noop_5bd39c,
    0x005bc8b5u, 0x00000001u
};

const uintptr_t display_driver_uled_option_type0[16] = {
    (uintptr_t)&display_driver_uled_option_type0_irq_592658,
    0x00592f9bu,
    (uintptr_t)&display_driver_uled_option_type0_setup_592680,
    (uintptr_t)&display_driver_uled_option_type0_enable_5926b4,
    0x00593201u, 0x0059328du, 0x00592e9du, 0x005931c1u,
    0x00593335u, 0x00592aa9u, 0x00592debu, 0x00592cb5u,
    0x005936a5u, 0x00593751u, 0x00000000u, 0x00000000u
};

_Static_assert(sizeof display_driver_uled_option_type1 == 64u, "uLED option size");
_Static_assert(sizeof display_driver_uled_option_type0 == 64u, "uLED option size");
