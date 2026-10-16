/* Native QK_activate_ 0x311554..0x3115e4, pinned QP/C comparator.
 * Controller objects and IRQ behavior require producing initialization/ABI.
 */
#include <stdint.h>
struct qk_prefix { volatile uint8_t active, next, lock; uint8_t gap[3]; volatile uint16_t ready; };
extern uint32_t opencfw_em9305_log2p1(uint16_t ready);
extern void opencfw_em9305_assert(uint32_t module, uint32_t line);
extern void *opencfw_em9305_active_get(void *active); /* 0x310d38 */
extern void opencfw_em9305_event_gc(void *event); /* 0x310fb8 */
void opencfw_em9305_qk_activate(void)
{
    volatile struct qk_prefix *const state = (volatile struct qk_prefix *)(uintptr_t)UINT32_C(0x801394);
    void *volatile *const active_table = (void *volatile *)(uintptr_t)UINT32_C(0x80131c);
    const uint8_t previous = state->active;
    uint32_t candidate = state->next;
    if (candidate == 0) opencfw_em9305_assert(UINT32_C(0x33451c), 500);
    state->next = 0;
    for (;;) {
        state->active = (uint8_t)candidate;
        const uint8_t priority = (uint8_t)candidate;
        void *const active = active_table[priority];
        __asm__ volatile("seti 0" ::: "memory");
        void *const event = opencfw_em9305_active_get(active);
        void **const vtable = *(void ***)active;
        void (*const dispatch)(void *,void *) = (void (*)(void *,void *))vtable[1];
        dispatch(active,event);
        opencfw_em9305_event_gc(event);
        __asm__ volatile("clri 0\n\tsync" ::: "memory");
        if (*(void *volatile *)((uint8_t *)active + 12) == 0) {
            const uint32_t ready = state->ready;
            const uint32_t index = (uint32_t)priority - 1u;
            uint32_t cleared;
            __asm__ volatile("bclr %0,%1,%2" : "=r"(cleared) : "r"(ready),"r"(index));
            state->ready = (uint16_t)cleared;
        }
        candidate = opencfw_em9305_log2p1(state->ready);
        const uint8_t next = (uint8_t)candidate;
        if (previous >= next || state->lock >= next) break;
        if (next >= 17) opencfw_em9305_assert(UINT32_C(0x33451c),510);
        if (next == 0) break;
    }
    state->active = previous;
}
