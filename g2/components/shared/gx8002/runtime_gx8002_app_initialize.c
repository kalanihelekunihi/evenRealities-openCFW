/* SPDX-License-Identifier: MIT */
/* Recovered initialization at package 0x12260. Registration and watchdog
 * implementations remain separate recovery dependencies. */
#include <stdint.h>
#include <stddef.h>
#include <lvp_app.h>
#include <lvp_queue.h>
extern LVP_APP *open_cfw_gx8002_app_core_ops;
extern LVP_QUEUE open_cfw_gx8002_app_event_queue;
extern unsigned char open_cfw_gx8002_app_event_buffer[64];
#include "runtime_gx8002_power_registration.h"
extern int open_cfw_gx8002_app_suspend(void *);
extern int open_cfw_gx8002_app_resume(void *);
extern int open_cfw_gx8002_watchdog_callback(int, void *);
extern void open_cfw_gx8002_watchdog_initialize(uint16_t, uint16_t, int (*)(int, void *), void *);
static const char suspend_name[] = "_LvpAppSuspend";
static const char resume_name[] = "_LvpAppResume";

int open_cfw_gx8002_app_initialize(void)
{
    LvpQueueInit(&open_cfw_gx8002_app_event_queue,
                 open_cfw_gx8002_app_event_buffer, 64, 8);
    if (open_cfw_gx8002_app_core_ops && open_cfw_gx8002_app_core_ops->AppInit)
        (void)open_cfw_gx8002_app_core_ops->AppInit();
    struct open_cfw_app_power_registration suspend = {
        open_cfw_gx8002_app_suspend, (void *)suspend_name
    };
    struct open_cfw_app_power_registration resume = {
        open_cfw_gx8002_app_resume, (void *)resume_name
    };
    open_cfw_gx8002_register_suspend(&suspend);
    open_cfw_gx8002_register_resume(&resume);
    open_cfw_gx8002_watchdog_initialize(3000, 2999, open_cfw_gx8002_watchdog_callback, NULL);
    return 0;
}
