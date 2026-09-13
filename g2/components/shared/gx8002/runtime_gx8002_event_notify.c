/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_notification_stamp(void);
extern int open_cfw_gx8002_app_reply(uint32_t,uint32_t,uint32_t);
void open_cfw_gx8002_event_notify(uint32_t event)
{
    open_cfw_gx8002_notification_stamp();
    open_cfw_gx8002_app_reply(1,12,event);
}
