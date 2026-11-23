#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31ccf4..0x31ce0e: set up a periodic-sync/BIG receiver object from
 * its parameters. Clear the 124-byte state (+72) and the 44-byte schedule
 * node (+296), mark +321/+322, install the dispatch callbacks (+176, +180,
 * +324, +328), copy 76 bytes of the template at owner(+256)+176 and derive
 * the timing: anchor (+252 = params +4), window start (+248, -300/-30 us per
 * unit +10 depending on +12), packet time (native 0x312bc0 for PHY +56 plus
 * +20 * +17) at +308/+312 and the window margin (300/30 us) at +246. Then
 * widen the window (native 0x317ebc), refresh the channel state (native
 * 0x3257f4) and insert the node, advancing the 64-bit event counter (+0x20)
 * and the anchor by the interval (+16) until the schedule accepts it.
 * Returns the insert result. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_dispatch_child_312bc0(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_3257f4(uintptr_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_dispatch_callback_31ca0c(uint32_t);
extern uint32_t opencfw_em9305_dispatch_callback_31ceb4(uint32_t);
extern void opencfw_em9305_dispatch_callback_31d43c(uintptr_t,uintptr_t,uint32_t);
extern void opencfw_em9305_dispatch_callback_31cbb0(void);

uint32_t opencfw_em9305_dispatch_child_31ccf4(uintptr_t object, uintptr_t params)
{
    uintptr_t owner = *(volatile uint32_t *)(object + 256u);
    uintptr_t state = object + 72u;
    uintptr_t node = object + 296u;
    (void)opencfw_em9305_memset((void *)state, 0u, 0x7cu);
    (void)opencfw_em9305_memset((void *)node, 0u, 0x2cu);
    *(volatile uint8_t *)(object + 322u) = 1u;
    *(volatile uint8_t *)(object + 321u) = 1u;
    *(volatile uint32_t *)(object + 340u) = (uint32_t)state;
    *(volatile uint32_t *)(object + 328u) = (uint32_t)(uintptr_t)opencfw_em9305_dispatch_callback_31ca0c;
    *(volatile uint32_t *)(object + 324u) = (uint32_t)(uintptr_t)opencfw_em9305_dispatch_callback_31ceb4;
    *(volatile uint32_t *)(object + 332u) = (uint32_t)object;
    (void)opencfw_em9305_memcpy((void *)state, (const void *)(owner + 176u), 0x4cu);
    uint32_t count = *(volatile uint8_t *)(params + 17u);
    uint32_t spacing = *(volatile uint32_t *)(params + 20u);
    uint32_t packet = opencfw_em9305_dispatch_child_312bc0(*(volatile uint8_t *)(params + 56u), 7u);
    uint32_t anchor = *(volatile uint32_t *)(params + 4u);
    *(volatile uint32_t *)(object + 252u) = anchor;
    uint32_t coded = *(volatile uint8_t *)(params + 12u);
    packet += spacing * count;
    uint32_t units = *(volatile uint16_t *)(params + 10u);
    uint32_t step = coded == 0u ? (uint32_t)-30 : (uint32_t)-300;
    uint32_t start = *(volatile uint32_t *)(params + 4u) + step * units;
    uint32_t offset = *(volatile uint32_t *)(object + 264u);
    uint32_t policy = em9305_ram_805c5c.u32_805c98;
    *(volatile uint32_t *)(object + 248u) = start;
    uint32_t margin = *(volatile uint8_t *)(params + 12u) == 0u ? 30u : 300u;
    uint32_t window = anchor + offset - start + margin;
    *(volatile uint32_t *)(object + 180u) = (uint32_t)(uintptr_t)opencfw_em9305_dispatch_callback_31d43c;
    *(volatile uint32_t *)(object + 176u) = (uint32_t)(uintptr_t)opencfw_em9305_dispatch_callback_31cbb0;
    *(volatile uint32_t *)(object + 184u) = policy;
    *(volatile uint32_t *)(object + 312u) = packet;
    *(volatile uint32_t *)(object + 308u) = packet;
    *(volatile uint16_t *)(object + 246u) = (uint16_t)margin;
    for (;;) {
        uint32_t widening = opencfw_em9305_init_secondary_time_317ebc(
            window, *(volatile uint16_t *)(object + 244u));
        uint32_t span = *(volatile uint16_t *)(object + 246u) + widening * 2u;
        uint32_t base = *(volatile uint32_t *)(object + 252u);
        uint32_t delay = *(volatile uint32_t *)(object + 264u);
        uint32_t interval = *(volatile uint32_t *)(object + 16u);
        *(volatile uint32_t *)(object + 304u) = base - widening + delay;
        *(volatile uint32_t *)(object + 316u) = interval;
        *(volatile uint32_t *)(object + 172u) = span;
        (void)opencfw_em9305_dispatch_child_3257f4(object);
        uint32_t result = opencfw_em9305_associated_schedule_insert_312da4(node, 0u);
        if (result != 0u) return result;
        uint32_t low = *(volatile uint32_t *)(object + 0x20u);
        uint32_t high = *(volatile uint32_t *)(object + 0x24u);
        interval = *(volatile uint32_t *)(object + 16u);
        uint64_t events = (((uint64_t)high << 32) | low) + 1u;
        uint32_t next = *(volatile uint32_t *)(object + 252u) + interval;
        window += interval;
        *(volatile uint32_t *)(object + 0x20u) = (uint32_t)events;
        *(volatile uint32_t *)(object + 252u) = next;
        *(volatile uint32_t *)(object + 0x24u) = (uint32_t)(events >> 32);
    }
}
