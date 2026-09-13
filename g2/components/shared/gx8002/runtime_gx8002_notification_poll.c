/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_notification_time;
extern uint32_t open_cfw_gx8002_clock(void);
extern int open_cfw_gx8002_gpio_value(uint32_t, uint32_t);
int open_cfw_gx8002_notification_poll(void)
{
    if (open_cfw_gx8002_notification_time &&
        (uint32_t)(open_cfw_gx8002_clock() - open_cfw_gx8002_notification_time) > 60) {
        open_cfw_gx8002_gpio_value(2, 1);
        open_cfw_gx8002_notification_time = 0;
    }
    return 0;
}
