#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32ca74..0x32ca8e: copy the three parameter words at +4..+12
 * of the current command (((uintptr_t)&em9305_ram_805c5c + 0x10u)) into the record at +660..+668. */
void opencfw_em9305_child_32ca74(uintptr_t record)
{
    uintptr_t command=em9305_ram_805c5c.u32_805c6c;
    uint32_t first=*(volatile uint32_t *)(command+4u);
    uint32_t second=*(volatile uint32_t *)(command+8u);
    *(volatile uint32_t *)(record+660u)=first;
    uint32_t third=*(volatile uint32_t *)(command+12u);
    *(volatile uint32_t *)(record+664u)=second;
    *(volatile uint32_t *)(record+668u)=third;
}
