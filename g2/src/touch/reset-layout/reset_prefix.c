#include <stdint.h>

/* Stock 0x4674..0x467e calls a no-op, then 0x471c. The latter writes the
 * authenticated literal to the device register and masks interrupts.
 * The peripheral's physical response is outside this source contract. */
/* Stock 0x0000471C (touch_runtime_141c_handoff) */
void g2_touch_candidate_reset_prefix(void)
{
    *(volatile uint32_t *)0x40030038u = 0xaced8865u;
    __asm volatile ("cpsid i" ::: "memory");
}
