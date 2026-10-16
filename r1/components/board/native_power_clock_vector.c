/* Authenticated application vector slot16 (external IRQ0 / POWER_CLOCK). */
extern void POWER_CLOCK_IRQHandler(void);
void (*const r1_power_clock_irq0_vector)(void)
 __attribute__((section(".r1.clock.irq0.vector"),aligned(4)))=POWER_CLOCK_IRQHandler;
_Static_assert(sizeof(r1_power_clock_irq0_vector)==4,"native Thumb vector word");
