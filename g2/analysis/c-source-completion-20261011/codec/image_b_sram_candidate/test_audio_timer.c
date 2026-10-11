/* Bounded timer/delay arithmetic fixture; no original-byte or hardware run. */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

extern uint64_t gx8002_image_b_time_10005070(void);
extern void gx8002_image_b_delay_10005144(uint32_t duration);
extern void gx8002_image_b_delay_ms_10005194(uint32_t milliseconds);

static uint64_t raw_tick, step;
static uint32_t reads;

uint32_t gx8002_image_b_timer_test_read(uint32_t offset)
{
    if (offset == 0x44u) return (uint32_t)raw_tick;
    if (offset == 0x48u) {
        uint32_t high = (uint32_t)(raw_tick >> 32);
        raw_tick += step;
        ++reads;
        return high;
    }
    __builtin_trap();
}

static uint64_t expected_time(uint64_t raw)
{
    return (raw * UINT64_C(1000)) >> 10;
}

int main(void)
{
    static const uint64_t raw_cases[] = {
        0u, 1u, 1024u, UINT32_MAX, UINT64_C(0x100000000),
        UINT64_C(0x100000001), UINT64_C(0x100000000000), UINT64_MAX,
    };
    step = 0u;
    for (unsigned i = 0; i < sizeof(raw_cases) / sizeof(raw_cases[0]); ++i) {
        raw_tick = raw_cases[i];
        if (gx8002_image_b_time_10005070() != expected_time(raw_cases[i])) {
            fprintf(stderr, "time scale failed %u\n", i);
            return 1;
        }
    }
    static const uint32_t durations[] = {0u, 1u, 17u, 1000u, 10000u};
    for (unsigned i = 0; i < sizeof(durations) / sizeof(durations[0]); ++i) {
        raw_tick = 4096u;
        step = 1024u;
        reads = 0u;
        uint64_t initial = expected_time(raw_tick);
        uint64_t deadline = initial + 1u + durations[i];
        gx8002_image_b_delay_10005144(durations[i]);
        if (expected_time(raw_tick - step) < deadline || reads > 20u) {
            fprintf(stderr, "delay deadline failed %u (%" PRIu32 " reads)\n", i, reads);
            return 1;
        }
    }
    raw_tick = 4096u;
    step = 1024u;
    reads = 0u;
    gx8002_image_b_delay_ms_10005194(10u);
    if (expected_time(raw_tick - step) < expected_time(4096u) + 10001u || reads > 20u)
        return 1;
    puts("8 timer scales and 6 delay deadlines pass");
    return 0;
}
