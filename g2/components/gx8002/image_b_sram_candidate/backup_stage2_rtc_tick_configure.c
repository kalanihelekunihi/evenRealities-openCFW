/* Native image-B RTC tick setup 0x1000881c..0x1000885a.
 * The prescaler overflow logs and returns before IRQ registration; no
 * shortened or fabricated success path is used.
 */
#include <stdint.h>

extern void gx8002_image_b_platform_gate_10003be8(uint32_t,
                                                    uint32_t);
extern uint32_t gx8002_image_b_clock_frequency_10003cf0(uint32_t);
extern void gx8002_image_b_request_irq_10004844(
    uint32_t, int32_t (*)(int32_t, void *), uint32_t);
extern uint32_t gx8002_image_b_rtc_irq_100087dc(uint32_t);
extern int gx8002_image_b_heap_log_10009934(const char *, ...);

void gx8002_image_b_rtc_tick_configure_1000881c(void)
{
    volatile uint32_t *const rtc =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0003000);
    gx8002_image_b_platform_gate_10003be8(0u, 1u);
    rtc[3] = rtc[3] | 16u;
    uint32_t prescaler = gx8002_image_b_clock_frequency_10003cf0(0u);
    if (prescaler > UINT32_C(65535)) {
        (void)gx8002_image_b_heap_log_10009934(
            "RTC prescaler error!\n");
        return;
    }
    rtc[8] = prescaler;
    gx8002_image_b_request_irq_10004844(
        4u, (int32_t (*)(int32_t, void *))(uintptr_t)
            gx8002_image_b_rtc_irq_100087dc, 0u);
    rtc[3] = rtc[3] | 4u;
}
