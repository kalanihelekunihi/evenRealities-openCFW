/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct app_state { uint32_t limit; void *handle; uint32_t lock, countdown; };
extern struct app_state open_cfw_gx8002_app_state;
extern int printf(const char *,...);
extern int open_cfw_gx8002_power_lock(uint32_t lock);
const char open_cfw_gx8002_gpio_event_name[] __attribute__((aligned(1)))="gpio_callback";
const char open_cfw_gx8002_gpio_event_message[] __attribute__((aligned(1)))="[YW_APP]%s %d !\n";
int open_cfw_gx8002_app_gpio_event(void *argument)
{
    (void)argument;
    printf(open_cfw_gx8002_gpio_event_message,open_cfw_gx8002_gpio_event_name,124);
    open_cfw_gx8002_power_lock(open_cfw_gx8002_app_state.lock);
    open_cfw_gx8002_app_state.countdown=2000;
    return 0;
}
