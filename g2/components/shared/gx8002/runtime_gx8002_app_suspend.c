/* SPDX-License-Identifier: MIT */
/* Recovered callback dispatch using the pinned SDK application layout.
 * Not yet admitted to the firmware builder.
 */
#include <stddef.h>
#include <stdint.h>
#include <lvp_app.h>

#ifndef OPEN_CFW_GX8002_APP_HOST_TEST
_Static_assert(offsetof(LVP_APP, AppSuspend) == 16, "target callback ABI");
_Static_assert(offsetof(LVP_APP, suspend_priv) == 20, "target context ABI");

#endif
extern LVP_APP *open_cfw_gx8002_app_core_ops;

extern void open_cfw_gx8002_watchdog_stop(void);

int open_cfw_gx8002_app_suspend(void *unused)
{
    (void)unused;
    open_cfw_gx8002_watchdog_stop();
    LVP_APP *app = open_cfw_gx8002_app_core_ops;
    if (app && app->AppSuspend)
        (void)app->AppSuspend(app->suspend_priv);
    return 0;
}
