/* Contract regression checks, not execution of the stock ARC instruction. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "../../../components/em9305/qpc_scheduler_candidate/scheduler.c"
static uint32_t candidate, assertion_count;
static uint16_t observed_ready;
uint32_t opencfw_em9305_log2p1(uint16_t ready)
{
    observed_ready = ready;
    return candidate;
}
void opencfw_em9305_assert(uint32_t module, uint32_t line)
{
    assert(module == 0x33451c && line == 410);
    ++assertion_count;
}
int main(void)
{
    const struct {
        uint32_t candidate;
        uint8_t active, lock, expected, asserts;
    } tests[] = {
        {256, 0, 0, 0, 0}, {257, 0, 0, 1, 0},
        {511, 0, 0, 255, 1}, {17, 0, 0, 17, 1},
        {16, 0, 0, 16, 0}, {16, 16, 0, 0, 0},
        {16, 0, 16, 0, 0}, {17, 17, 0, 0, 0},
        {17, 0, 17, 0, 0}, {0xffffffff, 254, 0, 255, 1},
        {0xffffffff, 255, 0, 0, 0}, {0x123401, 0, 0, 1, 0}
    };
    for (unsigned i = 0; i < sizeof tests / sizeof tests[0]; ++i) {
        struct opencfw_qk_state state = {
            tests[i].active, 0xa5, tests[i].lock, {0x91, 0x92, 0x93}, 0xabcd
        };
        candidate = tests[i].candidate;
        assertion_count = 0;
        assert(opencfw_em9305_qk_sched_state(&state) == tests[i].expected);
        assert(state.next_priority == (tests[i].expected ? tests[i].expected : 0xa5));
        assert(assertion_count == tests[i].asserts && observed_ready == 0xabcd);
        assert(state.active_priority == tests[i].active && state.lock_priority == tests[i].lock);
        assert(state.unowned_3_5[0] == 0x91 && state.unowned_3_5[1] == 0x92 && state.unowned_3_5[2] == 0x93);
        assert(state.ready_set == 0xabcd);
    }
    puts("PASS: 12 scheduler contract cases; vendor arithmetic and stock execution untested");
    return 0;
}
