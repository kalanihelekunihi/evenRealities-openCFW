/* Recovered QK_sched_ control flow at 0x311634..0x31166c.
 * Sources: authenticated instruction listing and byte-narrowing correction
 * under pre-consolidation:g2/analysis/em9305-qpc-{source-binding,byte-narrowing-successor}-2026-10-09.
 * The producing APEX operation is an explicit hardware/port contract. Neither
 * ordinary C highest-bit arithmetic nor a presumed QP/C version substitutes it.
 * This experimental source is not a complete controller or admitted provider.
 */
#include <stddef.h>
#include <stdint.h>

struct opencfw_qk_state {
    volatile uint8_t active_priority;
    volatile uint8_t next_priority;
    volatile uint8_t lock_priority;
    uint8_t unowned_3_5[3];
    volatile uint16_t ready_set;
};
_Static_assert(offsetof(struct opencfw_qk_state, ready_set) == 6,
               "authenticated halfword load offset");

/* Typed C interface requirements, not claims about the vendor C ABI. The stock
 * custom instruction consumes R0 and produces R13; its port adapter is absent.
 * Assertion can return in the observed continuation, so it is not noreturn.
 */
extern uint32_t opencfw_em9305_log2p1(uint16_t ready_set);
extern void opencfw_em9305_assert(uint32_t module_address, uint32_t line);

uint32_t opencfw_em9305_qk_sched_state(struct opencfw_qk_state *state)
{
    const uint32_t candidate = opencfw_em9305_log2p1(state->ready_set);
    const uint8_t priority = (uint8_t)candidate;
    if (priority <= state->active_priority) {
        return 0;
    }
    if (priority <= state->lock_priority) {
        return 0;
    }
    if (priority >= 17) {
        opencfw_em9305_assert(UINT32_C(0x33451c), UINT32_C(410));
    }
    state->next_priority = (uint8_t)candidate;
    return (uint8_t)candidate;
}

/* Stock 0x00311634 (QK_sched_) */
uint32_t opencfw_em9305_qk_sched(void)
{
    return opencfw_em9305_qk_sched_state(
        (struct opencfw_qk_state *)(uintptr_t)UINT32_C(0x801394));
}
