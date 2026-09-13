/* SPDX-License-Identifier: MIT */
/* SDK application ABI recovered at package 0x18d4c.
 * Candidate: callback definitions now use SDK signatures; full descriptor
 * admission remains separate. See gx8002-application-callback-types.json.
 */
#include <stddef.h>
#include <lvp_app.h>
extern int open_cfw_gx8002_sample_app_init(void);
extern int open_cfw_gx8002_sample_event(APP_EVENT *);
extern int open_cfw_gx8002_i2s_request_tick(void);
extern int open_cfw_gx8002_app_gpio_suspend(void *);
extern int open_cfw_gx8002_app_gpio_resume(void *);
extern const char open_cfw_gx8002_sample_app_labels[];

LVP_APP open_cfw_gx8002_sample_application
    __attribute__((section(".data.sample_application"))) = {
    .app_name = open_cfw_gx8002_sample_app_labels,
    .AppInit = open_cfw_gx8002_sample_app_init,
    .AppEventResponse = open_cfw_gx8002_sample_event,
    .AppTaskLoop = open_cfw_gx8002_i2s_request_tick,
    /* Preserve the recovered slot order. The earlier GPIO helper names
     * describe their pin operations, not their role in this descriptor. */
    .AppSuspend = open_cfw_gx8002_app_gpio_resume,
    .suspend_priv = (void *)(open_cfw_gx8002_sample_app_labels + sizeof("sample app")),
    .AppResume = open_cfw_gx8002_app_gpio_suspend,
    .resume_priv = (void *)(open_cfw_gx8002_sample_app_labels +
                           sizeof("sample app") + sizeof("SampleAppSuspend"))
};
LVP_APP *open_cfw_gx8002_app_core_ops
    __attribute__((section(".data.app_core_ops"))) = &open_cfw_gx8002_sample_application;
_Static_assert(sizeof(LVP_APP) == 32, "application ABI");
_Static_assert(offsetof(LVP_APP, AppSuspend) == 16, "suspend slot");
_Static_assert(offsetof(LVP_APP, AppResume) == 24, "resume slot");
