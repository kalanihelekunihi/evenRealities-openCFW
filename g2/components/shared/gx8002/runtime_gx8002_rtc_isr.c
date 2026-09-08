/* SPDX-License-Identifier: MIT
 * Callback precedes the RTC acknowledgement read; its result is returned.
 */
#include <stdint.h>
typedef int (*rtc_callback_t)(int irq, void *argument);
struct rtc_callback_state {
    rtc_callback_t callback;
    void *argument;
};
extern volatile struct rtc_callback_state open_cfw_gx8002_rtc_callback_state;
int open_cfw_gx8002_rtc_isr(int irq, void *unused)
{
    (void)unused;
    rtc_callback_t callback = open_cfw_gx8002_rtc_callback_state.callback;
    int result = 0;
    if (callback)
        result = callback(irq, open_cfw_gx8002_rtc_callback_state.argument);
    (void)*(volatile uint32_t *)(uintptr_t)0xa0003018u;
    return result;
}
