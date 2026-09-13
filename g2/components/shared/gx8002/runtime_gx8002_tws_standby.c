/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip _LvpSetStandbyState/_LvpStandbyStateLoop,
 * lvp/lvp_mode_tws.c at 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd.
 * See NATIONALCHIP-TWS-NOTICE.txt. Recovered countdown configuration: 50.
 * Unsigned countdown preserves machine wrap on decrement, including zero. */
#include <stdint.h>
#include <stddef.h>
#include <lvp_queue.h>
extern struct {
    LVP_QUEUE queue;
    unsigned char buffer[56];
    uint32_t state;
    uint32_t countdown;
} open_cfw_gx8002_tws_standby_storage;
_Static_assert(offsetof(__typeof__(open_cfw_gx8002_tws_standby_storage),state)==76,"state ABI");
_Static_assert(offsetof(__typeof__(open_cfw_gx8002_tws_standby_storage),countdown)==80,"countdown ABI");
void open_cfw_gx8002_tws_set_standby(uint32_t state)
{
    open_cfw_gx8002_tws_standby_storage.state=state;
    if (state==2) open_cfw_gx8002_tws_standby_storage.countdown=50;
}
void open_cfw_gx8002_tws_standby_loop(void)
{
    if (open_cfw_gx8002_tws_standby_storage.state==2) {
        --open_cfw_gx8002_tws_standby_storage.countdown;
        if (!open_cfw_gx8002_tws_standby_storage.countdown)
            open_cfw_gx8002_tws_standby_storage.state=4;
    }
}
