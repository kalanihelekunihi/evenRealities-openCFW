/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10026314 main loop. Five XIP descendants and the
 * 0x10207a7c exit child remain explicit source contracts.
 */
#include <stdint.h>

extern void gx8002_xip_lvp_system_initialize_102078a4(void);
extern uint32_t gx8002_xip_lvp_init_mode_102085a4(uint32_t mode);
extern uint32_t gx8002_xip_app_initialize_10208cd4(void);
extern uint32_t gx8002_xip_mode_tick_102085f8(void);
extern void gx8002_xip_app_event_tick_10208d48(void);
extern void gx8002_xip_main_exit_10207a7c(void);

/* Stock 0x10026314 (gx8002_main) */
uint32_t gx8002_resident_main_26314(void)
{
    gx8002_xip_lvp_system_initialize_102078a4();
    (void)gx8002_xip_lvp_init_mode_102085a4(1u);
    (void)gx8002_xip_app_initialize_10208cd4();
    uint32_t tick;
    do {
        tick = gx8002_xip_mode_tick_102085f8();
        if (tick != 0u) gx8002_xip_app_event_tick_10208d48();
    } while (tick != 0u);
    gx8002_xip_main_exit_10207a7c();
    return tick;
}
