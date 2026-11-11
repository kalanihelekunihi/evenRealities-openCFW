#include <stdint.h>

/* Native 0x32ca20..0x32ca3c: copy the three configuration words at
 * +4/+8/+12 of the object at 0x805c6c into record words 165..167. */
void opencfw_em9305_child_32ca20(uintptr_t record)
{
    uintptr_t config=*(volatile uint32_t *)0x805c6cu;
    uint32_t first=*(volatile uint32_t *)(config+4u);
    uint32_t second=*(volatile uint32_t *)(config+8u);
    *(volatile uint32_t *)(record+660u)=first;
    uint32_t third=*(volatile uint32_t *)(config+12u);
    *(volatile uint32_t *)(record+664u)=second;
    *(volatile uint32_t *)(record+668u)=third;
}
