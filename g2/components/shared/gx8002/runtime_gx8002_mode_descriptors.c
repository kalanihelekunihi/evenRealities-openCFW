/* SPDX-License-Identifier: MIT */
#include <lvp_mode.h>
extern const LVP_MODE_INFO lvp_idle_mode_info;
extern int open_cfw_gx8002_tws_init(LVP_MODE_TYPE);
extern void open_cfw_gx8002_tws_done(LVP_MODE_TYPE);
extern void open_cfw_gx8002_tws_tick(void);
extern int open_cfw_gx8002_tws_buffer_init(void);
const LVP_MODE_INFO lvp_tws_mode_info __attribute__((section(".rodata.tws_info"))) = {
    .type=LVP_MODE_TWS, .init=open_cfw_gx8002_tws_init,
    .done=open_cfw_gx8002_tws_done, .tick=open_cfw_gx8002_tws_tick,
    .buffer_init=open_cfw_gx8002_tws_buffer_init
};
const LVP_MODE_INFO *const open_cfw_gx8002_mode_list[2] __attribute__((section(".rodata.mode_list"))) = {
    &lvp_idle_mode_info, &lvp_tws_mode_info
};
_Static_assert(sizeof(LVP_MODE_INFO)==20,"Mode descriptor ABI");
