#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_callback_31f9b0(uint32_t context, uint32_t event);

static uint32_t first_result, second_result, first_calls, second_calls;
static uint32_t last_base, last_event, first_mode, second_mode, last_context, last_code;
static uint32_t dispatch_kind, dispatch_calls;
static uint32_t mutate_first, mutate_second;

uint32_t opencfw_em9305_child_3191dc(uint32_t base, uint32_t event, uint32_t mode)
{
    ++first_calls; last_base = base; last_event = event; first_mode = mode;
    *(volatile uint8_t *)0x800002u = (uint8_t)mutate_first;
    return first_result;
}
uint32_t opencfw_em9305_child_319714(uint32_t base, uint32_t event, uint32_t mode)
{
    ++second_calls; last_base = base; last_event = event; second_mode = mode;
    *(volatile uint8_t *)0x800002u = (uint8_t)mutate_second;
    return second_result;
}
uint32_t opencfw_em9305_child_32a000(uint32_t context, uint32_t code)
{
    ++dispatch_calls; dispatch_kind = 1; last_context = context; last_code = code;
    return 0x32000000u | code;
}
uint32_t opencfw_em9305_child_31e4a0(uint32_t context, uint32_t code)
{
    ++dispatch_calls; dispatch_kind = 2; last_context = context; last_code = code;
    return 0x31000000u | code;
}

int main(void)
{
    uint8_t *record = mmap((void *)0x800000u, 0x1000u, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0);
    assert(record == (void *)0x800000u);
    unsigned cases = 0;
    for (unsigned active = 0; active < 2; ++active)
    for (unsigned mode = 0; mode < 2; ++mode)
    for (unsigned first = 0; first < 3; ++first)
    for (unsigned second = 0; second < 3; ++second)
    for (unsigned after_first = 0; after_first < 2; ++after_first)
    for (unsigned after_second = 0; after_second < 2; ++after_second) {
        record[0] = (uint8_t)active;
        record[2] = (uint8_t)mode;
        first_result = first == 0 ? 0u : first == 1 ? 30u : 7u;
        second_result = second == 0 ? 0u : second == 1 ? 30u : 9u;
        mutate_first = after_first;
        mutate_second = after_second;
        first_calls = second_calls = dispatch_calls = dispatch_kind = 0u;
        uint32_t result = opencfw_em9305_callback_31f9b0(0x800000u, 0x55aau);
        if (!active) {
            assert(result == 0u && first_calls == 0u && second_calls == 0u && dispatch_calls == 0u);
        } else {
            uint32_t code = first_result == 0u || second_result == 0u ? 12u
                          : first_result == 30u || second_result == 30u ? 14u : 13u;
            uint32_t dispatch_mode = first_result == 0u ? after_first : after_second;
            assert(first_calls == 1u);
            assert(second_calls == (first_result != 0u));
            assert(dispatch_calls == 1u && dispatch_kind == (dispatch_mode == 0u ? 2u : 1u));
            assert(last_base == 0x802810u && last_event == 0x55aau && first_mode == mode);
            if (second_calls) assert(second_mode == after_first);
            assert(last_context == 0x800000u && last_code == code);
            assert(result == ((dispatch_mode == 0u ? 0x31000000u : 0x32000000u) | code));
        }
        ++cases;
    }
    printf("PASS callback 31f9b0 %u branch fixtures\n", cases);
    return 0;
}
