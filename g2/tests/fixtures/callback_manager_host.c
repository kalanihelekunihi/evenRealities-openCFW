#include <stdint.h>
#include <stdlib.h>

static uint32_t allocations;
static uint32_t frees;
static uint32_t fail_allocation;
static uint32_t events[16];
static uint32_t event_count;

void *open_cfw_test_callback_alloc(size_t size)
{
    if (fail_allocation != 0u) {
        return NULL;
    }
    allocations++;
    return malloc(size);
}

void open_cfw_test_callback_free(void *allocation)
{
    if (allocation != NULL) {
        frees++;
        free(allocation);
    }
}

void open_cfw_test_callback_host_reset(void)
{
    allocations = 0u;
    frees = 0u;
    fail_allocation = 0u;
    event_count = 0u;
}

void open_cfw_test_callback_host_fail_alloc(uint32_t fail)
{
    fail_allocation = fail;
}

uint32_t open_cfw_test_callback_host_word(uint32_t index)
{
    if (index == 0u) {
        return allocations;
    }
    if (index == 1u) {
        return frees;
    }
    if (index == 2u) {
        return event_count;
    }
    index -= 3u;
    return index < event_count ? events[index] : 0u;
}

void open_cfw_test_callback_one(uint32_t event, uintptr_t value)
{
    events[event_count++] = 0x10000000u | event;
    events[event_count++] = (uint32_t)value;
}

void open_cfw_test_callback_two(uint32_t event, uintptr_t value)
{
    events[event_count++] = 0x20000000u | event;
    events[event_count++] = (uint32_t)value;
}
