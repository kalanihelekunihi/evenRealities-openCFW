/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void gx_clock_set_module_enable(unsigned int module, unsigned int enable);
extern unsigned int gx_clock_get_module_frequence(unsigned int module);
extern void gx_request_irq(unsigned int irq, int (*handler)(int, void *), void *argument);
extern int printf_(const char *format, ...);
extern int open_cfw_gx8002_rtc_isr(int irq, void *argument);
extern void open_cfw_gx8002_rtc_start_tick(void);
extern const char open_cfw_gx8002_rtc_error[];
void open_cfw_gx8002_rtc_init(void)
{
    gx_clock_set_module_enable(0, 1);
    volatile uint32_t *control = (volatile uint32_t *)(uintptr_t)0xa000300cu;
    *control = *control | 16u;
    unsigned int frequency = gx_clock_get_module_frequence(0);
    if (frequency >= 65536u) {
        printf_(open_cfw_gx8002_rtc_error);
        return;
    }
    *(volatile uint32_t *)(uintptr_t)0xa0003020u = frequency;
    gx_request_irq(4, open_cfw_gx8002_rtc_isr, (void *)0);
    open_cfw_gx8002_rtc_start_tick();
}
