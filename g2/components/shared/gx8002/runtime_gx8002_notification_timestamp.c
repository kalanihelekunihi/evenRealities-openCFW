/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_notification_gpio_value(uint32_t,uint32_t);
extern uint32_t open_cfw_gx8002_notification_clock(void);
extern uint32_t open_cfw_gx8002_notification_timestamp;
void open_cfw_gx8002_notification_stamp(void)
{
    open_cfw_gx8002_notification_gpio_value(2,0);
    open_cfw_gx8002_notification_timestamp=open_cfw_gx8002_notification_clock();
}
