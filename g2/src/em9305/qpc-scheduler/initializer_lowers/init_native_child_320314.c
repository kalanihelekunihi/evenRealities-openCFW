#include <stdint.h>

/* Native 0x320314..0x320356: advance the link's retry counter (+242) while
 * either request byte (+1/+2) is set: with the hold flag (+241) the abort
 * (native 0x325e84, reason 3) is raised from the second retry on, without
 * it on any non-zero count. With no request and no hold, run native
 * 0x320354 instead. */
extern uint32_t opencfw_em9305_child_325e84(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_child_320354(uintptr_t);

void opencfw_em9305_child_320314(uintptr_t context)
{
    uintptr_t link = *(volatile uint32_t *)(context + 0x24u);
    if (*(volatile uint8_t *)(link + 2u) != 0u || *(volatile uint8_t *)(link + 1u) != 0u) {
        uint32_t count = *(volatile uint8_t *)(link + 242u) + 1u;
        uint32_t hold = *(volatile uint8_t *)(link + 241u);
        *(volatile uint8_t *)(link + 242u) = (uint8_t)count;
        count &= 0xffu;
        if (hold != 0u ? count >= 2u : count != 0u)
            (void)opencfw_em9305_child_325e84(link, 3u);
        return;
    }
    if (*(volatile uint8_t *)(link + 241u) == 0u)
        (void)opencfw_em9305_child_320354(link);
}
