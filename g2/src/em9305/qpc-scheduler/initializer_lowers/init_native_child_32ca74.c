#include <stdint.h>

/* Native 0x32ca74..0x32ca8e: copy the three parameter words at +4..+12
 * of the current command (0x805c6c) into the record at +660..+668. */
void opencfw_em9305_child_32ca74(uintptr_t record)
{
    uintptr_t command=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
    uint32_t first=*(volatile uint32_t *)(command+4u);
    uint32_t second=*(volatile uint32_t *)(command+8u);
    *(volatile uint32_t *)(record+660u)=first;
    uint32_t third=*(volatile uint32_t *)(command+12u);
    *(volatile uint32_t *)(record+664u)=second;
    *(volatile uint32_t *)(record+668u)=third;
}
