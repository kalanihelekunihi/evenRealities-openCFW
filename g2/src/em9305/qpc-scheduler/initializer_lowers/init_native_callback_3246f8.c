#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3246f8..0x32472e: store the two parameter bytes at +506/+505 and
 * whether the configured version byte (*((uintptr_t)&em9305_ram_805c5c + 0x50u) +4) is at least 13 at +777.
 * If the procedure flag +504 was clear, set it and start native 0x32dab4 on
 * it with the fourth argument. */
extern uint32_t opencfw_em9305_child_32dab4(uintptr_t,uint32_t);

void opencfw_em9305_callback_3246f8(uintptr_t record, uint32_t first, uint32_t second,
                                    uint32_t argument)
{
    uintptr_t config = em9305_ram_805c5c.u32_805cac;
    volatile uint8_t *active = (volatile uint8_t *)(record + 504u);
    uint32_t was_active = *active;
    int32_t version = *(volatile uint8_t *)(config + 4u);
    *(volatile uint8_t *)(record + 506u) = (uint8_t)first;
    *(volatile uint8_t *)(record + 505u) = (uint8_t)second;
    *(volatile uint8_t *)(record + 777u) = version >= 13;
    if (was_active != 0u) return;
    *active = 1u;
    (void)opencfw_em9305_child_32dab4((uintptr_t)active, argument);
}
