#include <stdint.h>

/* Native 0x32b618 is one ARC unconditional branch to 0x32b9a4 (a tail
 * call: the callback receives the caller's argument and return address). */
extern uint32_t opencfw_em9305_associated_cycle_callback_32b9a4(uintptr_t);

uint32_t opencfw_em9305_associated_cycle_tail_32b618(uintptr_t record)
{
    return opencfw_em9305_associated_cycle_callback_32b9a4(record);
}
