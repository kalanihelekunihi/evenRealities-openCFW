#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32ca3c..0x32ca74: terminate reception (reason 0x49) when the
 * global event counter at ((uintptr_t)&em9305_ram_8027e0 + 0x46u) is 0x7fff or more ahead of the
 * record's counter (+262), then copy the three global words at
 * ((uintptr_t)&em9305_ram_8027e0 + 0x3cu)..((uintptr_t)&em9305_ram_8027e0 + 0x44u) into record words 168..170. */
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t source,
                                                        uint32_t reason);

void opencfw_em9305_child_32ca3c(uintptr_t record)
{
    uint32_t local=*(volatile uint16_t *)(record+262u);
    uint32_t global=*(volatile uint16_t *)((uintptr_t)&em9305_ram_8027e0 + 0x46u);
    if((uint16_t)(global-local)>=0x7fffu)
        (void)opencfw_em9305_receive_terminate_325c08(record,0x49u);
    uint32_t first=*(volatile uint32_t *)((uintptr_t)&em9305_ram_8027e0 + 0x3cu);
    uint32_t second=*(volatile uint32_t *)((uintptr_t)&em9305_ram_8027e0 + 0x40u);
    uint32_t third=*(volatile uint32_t *)((uintptr_t)&em9305_ram_8027e0 + 0x44u);
    *(volatile uint32_t *)(record+672u)=first;
    *(volatile uint32_t *)(record+676u)=second;
    *(volatile uint32_t *)(record+680u)=third;
}
