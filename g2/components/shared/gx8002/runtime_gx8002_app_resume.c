/* SPDX-License-Identifier: MIT */
/* Recovered callback dispatch using the pinned SDK application layout.
 * Not yet admitted to the firmware builder.
 */
#include <stddef.h>
#include <stdint.h>
#include <lvp_app.h>

#ifndef OPEN_CFW_GX8002_APP_HOST_TEST
_Static_assert(offsetof(LVP_APP, AppResume) == 24, "target callback ABI");
_Static_assert(offsetof(LVP_APP, resume_priv) == 28, "target context ABI");

#endif
extern LVP_APP *open_cfw_gx8002_app_core_ops;

int open_cfw_gx8002_app_resume(void *unused)
{
    (void)unused;
    LVP_APP *app = open_cfw_gx8002_app_core_ops;
    if (app && app->AppResume)
        (void)app->AppResume(app->resume_priv);
    return 0;
}
