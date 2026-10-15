/* Partial source-owned S200 uLED option records. Fifteen callbacks use C symbols;
 * the other 14 distinct callback addresses remain authenticated native values.
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
extern uint32_t display_driver_uled_type1_pre_5bcb6c(void);
extern uint32_t display_driver_uled_type0_pre_593200(void);
extern uint32_t display_driver_uled_type0_frame_start_5931c0(void);
extern uint32_t display_driver_uled_type1_frame_start_5bcb28(void);
extern uint32_t display_driver_uled_type1_finish_5bcbb4(void);
extern uint32_t display_driver_uled_type0_finish_59328c(void);
extern uint32_t display_driver_uled_type0_aux_finish_5936a4(void);

const uintptr_t display_driver_uled_option_type1[16] = {
    (uintptr_t)&display_driver_uled_option_type1_irq_5bbd48,
    0x005bc76fu,
    (uintptr_t)&display_driver_uled_option_type1_setup_5bbd70,
    (uintptr_t)&display_driver_uled_option_type1_enable_5bbda4,
    (uintptr_t)&display_driver_uled_type1_pre_5bcb6c, (uintptr_t)&display_driver_uled_type1_finish_5bcbb4, 0x005bc6afu, (uintptr_t)&display_driver_uled_type1_frame_start_5bcb28,
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
    (uintptr_t)&display_driver_uled_type0_pre_593200, (uintptr_t)&display_driver_uled_type0_finish_59328c, 0x00592e9du, (uintptr_t)&display_driver_uled_type0_frame_start_5931c0,
    0x00593335u, 0x00592aa9u, 0x00592debu, 0x00592cb5u,
    (uintptr_t)&display_driver_uled_type0_aux_finish_5936a4, 0x00593751u, 0x00000000u, 0x00000000u
};

_Static_assert(sizeof display_driver_uled_option_type1 == 64u, "uLED option size");
_Static_assert(sizeof display_driver_uled_option_type0 == 64u, "uLED option size");
