#include <stdint.h>

/* Native 0x315958..0x315972: set bit 17 of the record's flag word (+636),
 * then run native 0x32ca74 and 0x31640c on the record. */
extern uint32_t opencfw_em9305_child_32ca74(uintptr_t);
extern uint32_t opencfw_em9305_child_31640c(uintptr_t);

uint32_t opencfw_em9305_child_315958(uintptr_t record)
{
    volatile uint32_t *flags = (volatile uint32_t *)(record + 636u);
    *flags = *flags | (1u << 17);
    (void)opencfw_em9305_child_32ca74(record);
    return opencfw_em9305_child_31640c(record);
}
