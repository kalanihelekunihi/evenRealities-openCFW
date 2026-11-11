#include <stdint.h>

/* Native 0x3257f4..0x325854: refresh the channel state of a scan context.
 * Each of the byte(+52) sub-records listed from +56 gets its state byte
 * +177 from native 0x30e5a4 on its block +120; the context block +352 then
 * yields byte +409. Byte +73 mirrors the state of the first sub-record
 * (role byte +3 == 1) or of the record at +256, and is returned. */
extern uint32_t opencfw_em9305_dispatch_child_30e5a4(uintptr_t,uint32_t,uint32_t,uint32_t);

uint32_t opencfw_em9305_dispatch_child_3257f4(uintptr_t context)
{
    uint32_t count = *(volatile uint8_t *)(context + 52u);
    if (count != 0u) {
        volatile uint32_t *slot = (volatile uint32_t *)(context + 56u);
        uint32_t index = 0u;
        do {
            uintptr_t sub = *slot++;
            if (sub != 0u) {
                uint32_t state = opencfw_em9305_dispatch_child_30e5a4(
                    sub + 120u, *(volatile uint16_t *)(context + 0x20u), 0u, 1u);
                count = *(volatile uint8_t *)(context + 52u);
                *(volatile uint8_t *)(sub + 177u) = (uint8_t)state;
            }
        } while (++index < count);
    }
    uint32_t state = opencfw_em9305_dispatch_child_30e5a4(
        context + 352u, *(volatile uint16_t *)(context + 0x20u), 0u, 1u);
    uint32_t role = *(volatile uint8_t *)(context + 3u);
    *(volatile uint8_t *)(context + 409u) = (uint8_t)state;
    uintptr_t source = *(volatile uint32_t *)(context + (role == 1u ? 56u : 256u));
    uint32_t mirrored = *(volatile uint8_t *)(source + 177u);
    *(volatile uint8_t *)(context + 73u) = (uint8_t)mirrored;
    return mirrored;
}
