/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp_kws lvp/lvp_mode_idle.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2019 NationalChip Co., Ltd
 * See NATIONALCHIP-IDLE-NOTICE.txt. The empty tick and successful buffer
 * initialization are original upstream/stock behavior, not missing services. */
#include <lvp_mode.h>
#include <stddef.h>
extern int printf(const char *, ...);
const char open_cfw_gx8002_idle_exit_message[] __attribute__((aligned(1))) = "[IDLE]Exit IDLE mode\n";
const char open_cfw_gx8002_idle_init_message[] __attribute__((aligned(1))) = "[IDLE]Init IDLE mode\n";
void open_cfw_gx8002_idle_tick(void) {}
int open_cfw_gx8002_idle_buffer_init(void) { return 0; }
void open_cfw_gx8002_idle_done(LVP_MODE_TYPE next)
{
    (void)next;
    printf(open_cfw_gx8002_idle_exit_message);
}
int open_cfw_gx8002_idle_init(LVP_MODE_TYPE previous)
{
    (void)previous;
    printf(open_cfw_gx8002_idle_init_message);
    return 0;
}
_Static_assert(sizeof(LVP_MODE_INFO) == 20, "recovered mode object size");
_Static_assert(offsetof(LVP_MODE_INFO, type) == 0, "type offset");
_Static_assert(offsetof(LVP_MODE_INFO, init) == 4, "init offset");
_Static_assert(offsetof(LVP_MODE_INFO, done) == 8, "done offset");
_Static_assert(offsetof(LVP_MODE_INFO, tick) == 12, "tick offset");
_Static_assert(offsetof(LVP_MODE_INFO, buffer_init) == 16, "buffer offset");
const LVP_MODE_INFO lvp_idle_mode_info = {
    .type = LVP_MODE_IDLE,
    .init = open_cfw_gx8002_idle_init,
    .done = open_cfw_gx8002_idle_done,
    .tick = open_cfw_gx8002_idle_tick,
    .buffer_init = open_cfw_gx8002_idle_buffer_init
};
