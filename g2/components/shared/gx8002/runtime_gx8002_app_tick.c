/* SPDX-License-Identifier: MIT */
/* Recovered event tick; UART service dependency remains under investigation. */
#include <lvp_app.h>
#include <lvp_queue.h>
extern LVP_APP *open_cfw_gx8002_app_core_ops;
extern LVP_QUEUE open_cfw_gx8002_app_event_queue;
extern int open_cfw_gx8002_uart_async_tick(void);
extern void open_cfw_gx8002_watchdog_ping(void);

int LvpAppEventTick(void)
{
    APP_EVENT event = {0};
    if (LvpQueueGet(&open_cfw_gx8002_app_event_queue, (unsigned char *)&event)) {
        if (open_cfw_gx8002_app_core_ops && open_cfw_gx8002_app_core_ops->AppEventResponse)
            (void)open_cfw_gx8002_app_core_ops->AppEventResponse(&event);
    }
    if (open_cfw_gx8002_app_core_ops && open_cfw_gx8002_app_core_ops->AppTaskLoop)
        (void)open_cfw_gx8002_app_core_ops->AppTaskLoop();
    (void)open_cfw_gx8002_uart_async_tick();
    open_cfw_gx8002_watchdog_ping();
    return 0;
}
