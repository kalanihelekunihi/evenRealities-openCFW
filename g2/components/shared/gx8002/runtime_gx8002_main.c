/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp_kws lvp/main.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd
 * See NATIONALCHIP-MAIN-NOTICE.txt. Shipped initial mode is TWS (1).
 * Stack monitoring is absent from the recovered call sequence. */
#include <lvp_mode.h>
#include <app_core/lvp_app_core.h>
extern void LvpSystemInit(void);
extern void LvpSystemDone(void);
int open_cfw_gx8002_main(void)
{
    LvpSystemInit();
    LvpInitMode(LVP_MODE_TWS);
    LvpInitializeAppEvent();
    while (LvpModeTick())
        LvpAppEventTick();
    LvpSystemDone();
    return 0;
}
