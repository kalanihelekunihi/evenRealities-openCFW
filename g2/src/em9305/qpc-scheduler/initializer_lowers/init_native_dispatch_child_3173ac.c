#include <stdint.h>

/* Native 0x3173ac..0x317418: advance the nested scan counters. counters[0]
 * counts ticks up to config +52; each wrap advances the event count
 * counters[4] and the sub-slot counters[1] (period config +24). A sub-slot
 * wrap advances counters[3] while the event count exceeds the slot budget
 * (config +27 * +24), otherwise the cycle counters[2] (period config +27).
 * Returns 1 while ticking or while the event count is below config +25. */
uint32_t opencfw_em9305_dispatch_child_3173ac(uintptr_t config, uintptr_t counters)
{
    const volatile uint8_t *limit = (const volatile uint8_t *)config;
    volatile uint8_t *count = (volatile uint8_t *)counters;
    uint32_t tick = count[0] + 1u;
    uint32_t ticks = limit[52];
    count[0] = (uint8_t)tick;
    if ((uint8_t)tick < ticks) return 1u;
    uint32_t events = count[4] + 1u;
    uint32_t slot = count[1] + 1u;
    uint32_t slots = limit[24];
    uint32_t cycles = limit[27];
    uint32_t budget = cycles * slots;
    count[4] = (uint8_t)events;
    events &= 0xffu;
    count[1] = (uint8_t)slot;
    slot &= 0xffu;
    count[0] = 0u;
    if (slot >= slots) {
        if (budget < events) {
            uint32_t overflow = count[3];
            count[1] = 0u;
            count[3] = (uint8_t)(overflow + 1u);
        } else {
            uint32_t cycle = count[2] + 1u;
            count[1] = 0u;
            count[2] = (uint8_t)cycle;
            if ((uint8_t)cycle >= cycles) count[2] = 0u;
        }
    }
    return events < limit[25] ? 1u : 0u;
}
