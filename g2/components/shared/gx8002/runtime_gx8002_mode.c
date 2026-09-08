/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp_kws lvp/lvp_mode.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2021 NationalChip Co., Ltd
 * See NATIONALCHIP-MODE-NOTICE.txt.
 * The shipped list contains IDLE and TWS. Callback calls can change the
 * selected index and loop flag, so those state reads must remain live. */
#include <lvp_mode.h>
extern const LVP_MODE_INFO lvp_idle_mode_info, lvp_tws_mode_info;
extern const LVP_MODE_INFO *const open_cfw_gx8002_mode_list[2];
extern volatile struct { int loop; int index; } open_cfw_gx8002_mode_state;

LVP_MODE_TYPE LvpInitMode(LVP_MODE_TYPE type)
{
    LVP_MODE_TYPE first = lvp_idle_mode_info.type;
    open_cfw_gx8002_mode_state.loop = 1;
    open_cfw_gx8002_mode_state.index = 0;
    int selected = 0;
    if (type == first)
        goto select;
    if (type != lvp_tws_mode_info.type)
        goto initialize;
    selected = 1;
select:
    open_cfw_gx8002_mode_state.index = selected;
initialize:
    open_cfw_gx8002_mode_list[open_cfw_gx8002_mode_state.index]->buffer_init();
    open_cfw_gx8002_mode_list[open_cfw_gx8002_mode_state.index]->init(LVP_MODE_INIT_FLAG);
    return open_cfw_gx8002_mode_list[open_cfw_gx8002_mode_state.index]->type;
}

int LvpModeTick(void)
{
    LVP_MODE_TICK tick = open_cfw_gx8002_mode_list[open_cfw_gx8002_mode_state.index]->tick;
    if (tick)
        tick();
    return open_cfw_gx8002_mode_state.loop;
}
