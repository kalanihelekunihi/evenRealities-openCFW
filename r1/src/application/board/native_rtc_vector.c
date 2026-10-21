/* Source-owned RTC2/IRQ36 vector word authenticated at native 0x270d0. */
typedef void (*r1_rtc_irq_fn)(void);
extern void RTC2_IRQHandler(void);
const r1_rtc_irq_fn r1_rtc_irq36_vector __attribute__((section(".r1.rtc.irq36.vector")))=RTC2_IRQHandler;
