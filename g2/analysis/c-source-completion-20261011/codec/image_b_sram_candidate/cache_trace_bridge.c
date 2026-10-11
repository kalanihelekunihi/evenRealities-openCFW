/* Host-only recorder for cache range MMIO writes. */
#include <stdint.h>

static uint32_t commands[65536];
static uint32_t used;

void gx8002_image_b_cache_trace_emit(uint32_t command)
{
    if (used < 65536u) commands[used++] = command;
}

void gx8002_cache_trace_reset(void) { used = 0u; }
uint32_t gx8002_cache_trace_count(void) { return used; }
uint32_t gx8002_cache_trace_at(uint32_t index) { return commands[index]; }
