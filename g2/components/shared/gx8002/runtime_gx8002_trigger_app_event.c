/* SPDX-License-Identifier: MIT */
/* Stock event ingress: queue failure is deliberately not propagated.
 * Target placement is checked separately; no optional SDK event filters here.
 */
#include <lvp_app_core.h>
#include <lvp_queue.h>
extern LVP_QUEUE open_cfw_gx8002_app_event_queue;
int LvpTriggerAppEvent(APP_EVENT *event)
{
    (void)LvpQueuePut(&open_cfw_gx8002_app_event_queue,
                      (const unsigned char *)event);
    return 0;
}
