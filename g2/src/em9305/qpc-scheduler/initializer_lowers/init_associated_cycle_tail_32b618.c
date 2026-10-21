#include <stdint.h>

/* Native 0x32b618 is one ARC unconditional branch to 0x32b9a4.  The
 * callback receives the caller's live registers and return address. */
extern uint32_t opencfw_em9305_associated_cycle_callback_32b9a4(uintptr_t);

__attribute__((naked))
uint32_t opencfw_em9305_associated_cycle_tail_32b618(uintptr_t record __attribute__((unused)))
{
    __asm__ volatile("b opencfw_em9305_associated_cycle_callback_32b9a4");
}
