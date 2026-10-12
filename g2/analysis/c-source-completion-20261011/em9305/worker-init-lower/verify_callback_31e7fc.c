#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_callback_31e7fc(void);
static unsigned probes, dispatches;
static uint32_t last_field, last_record, last_code;
static uint32_t probe_result;
uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t field)
{ ++probes; last_field = field; return probe_result; }
uint32_t opencfw_em9305_child_31e4a0(uint32_t record, uint32_t code)
{ ++dispatches; last_record = record; last_code = code; return 0xaabbccdd; }

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) == (void *)0x800000u);
    *(volatile uint32_t *)0x805cacu = 0x804000u;
    *(volatile uint32_t *)0x805c70u = 0x807000u;
    for (unsigned n = 0; n < 4; ++n)
    for (unsigned active = 0; active < 2; ++active)
    for (unsigned probe = 0; probe < 2; ++probe)
    for (unsigned mode = 0; mode < 2; ++mode) {
        memset((void *)0x807000u, 0, 4u * 912u);
        *(volatile uint8_t *)0x804022u = (uint8_t)n;
        for (unsigned i = 0; i < n; ++i) {
            *(volatile uint8_t *)(uintptr_t)(0x807000u + i * 912u) = (uint8_t)active;
            *(volatile uint8_t *)(uintptr_t)(0x807000u + i * 912u + 2u) = (uint8_t)mode;
        }
        probes = dispatches = 0u;
        probe_result = probe;
        assert(opencfw_em9305_callback_31e7fc() == n);
        assert(probes == (active ? n : 0u));
        assert(dispatches == (active && !probe && !mode ? n : 0u));
        if (active && n) assert(last_field == 0x807000u + (n - 1u) * 912u + 360u);
        if (dispatches) {
            assert(last_record == 0x807000u + (n - 1u) * 912u);
            assert(last_code == 61u);
        }
    }
    puts("PASS callback 31e7fc 32 branch fixtures");
    return 0;
}
