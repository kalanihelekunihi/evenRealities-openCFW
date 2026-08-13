unsigned int open_cfw_test_ring_fill_interrupt_mask;
unsigned int open_cfw_test_ring_fill_enter_count;
unsigned int open_cfw_test_ring_fill_exit_count;
unsigned int open_cfw_test_ring_fill_exit_mask;
unsigned int open_cfw_test_ring_fill_read_result;
unsigned int open_cfw_test_ring_fill_read_count_value;
unsigned int open_cfw_test_ring_fill_write_result;
unsigned int open_cfw_test_ring_fill_read_calls;
unsigned int open_cfw_test_ring_fill_write_calls;
void *open_cfw_test_ring_fill_read_handle;
void *open_cfw_test_ring_fill_read_destination;
unsigned int open_cfw_test_ring_fill_read_capacity;
unsigned int *open_cfw_test_ring_fill_read_count_pointer;
void *open_cfw_test_ring_fill_write_ring;
const void *open_cfw_test_ring_fill_write_source;
unsigned int open_cfw_test_ring_fill_write_count;
unsigned char open_cfw_test_ring_fill_write_bytes[32];
unsigned int open_cfw_test_ring_fill_trace[4];
unsigned int open_cfw_test_ring_fill_trace_count;

void open_cfw_test_ring_fill_reset(void)
{
    unsigned int index;

    open_cfw_test_ring_fill_interrupt_mask = 0U;
    open_cfw_test_ring_fill_enter_count = 0U;
    open_cfw_test_ring_fill_exit_count = 0U;
    open_cfw_test_ring_fill_exit_mask = 0xFFFFFFFFU;
    open_cfw_test_ring_fill_read_result = 0U;
    open_cfw_test_ring_fill_read_count_value = 0U;
    open_cfw_test_ring_fill_write_result = 1U;
    open_cfw_test_ring_fill_read_calls = 0U;
    open_cfw_test_ring_fill_write_calls = 0U;
    open_cfw_test_ring_fill_read_handle = (void *)0;
    open_cfw_test_ring_fill_read_destination = (void *)0;
    open_cfw_test_ring_fill_read_capacity = 0U;
    open_cfw_test_ring_fill_read_count_pointer = (unsigned int *)0;
    open_cfw_test_ring_fill_write_ring = (void *)0;
    open_cfw_test_ring_fill_write_source = (const void *)0;
    open_cfw_test_ring_fill_write_count = 0U;
    open_cfw_test_ring_fill_trace_count = 0U;
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_ring_fill_write_bytes[index] = 0U;
    }
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_ring_fill_trace[index] = 0U;
    }
}

unsigned int open_cfw_test_ring_fill_critical_enter(void)
{
    ++open_cfw_test_ring_fill_enter_count;
    open_cfw_test_ring_fill_trace[
        open_cfw_test_ring_fill_trace_count++
    ] = 1U;
    return open_cfw_test_ring_fill_interrupt_mask;
}

void open_cfw_test_ring_fill_critical_exit(unsigned int interrupt_mask)
{
    ++open_cfw_test_ring_fill_exit_count;
    open_cfw_test_ring_fill_exit_mask = interrupt_mask;
    open_cfw_test_ring_fill_trace[
        open_cfw_test_ring_fill_trace_count++
    ] = 4U;
}

unsigned int open_cfw_test_ring_fill_read(
    void *handle,
    void *destination,
    unsigned int capacity,
    unsigned int *read_count
)
{
    unsigned int index;

    ++open_cfw_test_ring_fill_read_calls;
    open_cfw_test_ring_fill_read_handle = handle;
    open_cfw_test_ring_fill_read_destination = destination;
    open_cfw_test_ring_fill_read_capacity = capacity;
    open_cfw_test_ring_fill_read_count_pointer = read_count;
    open_cfw_test_ring_fill_trace[
        open_cfw_test_ring_fill_trace_count++
    ] = 2U;
    for (index = 0U; index < capacity; ++index) {
        ((unsigned char *)destination)[index] =
            (unsigned char)(0x80U + index);
    }
    *read_count = open_cfw_test_ring_fill_read_count_value;
    return open_cfw_test_ring_fill_read_result;
}

unsigned int open_cfw_test_ring_fill_write(
    void *ring,
    const void *source,
    unsigned int count
)
{
    unsigned int index;

    ++open_cfw_test_ring_fill_write_calls;
    open_cfw_test_ring_fill_write_ring = ring;
    open_cfw_test_ring_fill_write_source = source;
    open_cfw_test_ring_fill_write_count = count;
    open_cfw_test_ring_fill_trace[
        open_cfw_test_ring_fill_trace_count++
    ] = 3U;
    for (index = 0U; index < count && index < 32U; ++index) {
        open_cfw_test_ring_fill_write_bytes[index] =
            ((const unsigned char *)source)[index];
    }
    return open_cfw_test_ring_fill_write_result;
}

#define OPEN_CFW_UI_DISPLAY_RING_FILL_CRITICAL_ENTER() \
    open_cfw_test_ring_fill_critical_enter()
#define OPEN_CFW_UI_DISPLAY_RING_FILL_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_test_ring_fill_critical_exit(interrupt_mask)
#define OPEN_CFW_UI_DISPLAY_RING_FILL_READ( \
    handle, \
    destination, \
    capacity, \
    read_count \
) \
    open_cfw_test_ring_fill_read( \
        (handle), \
        (destination), \
        (capacity), \
        (read_count) \
    )
#define OPEN_CFW_UI_DISPLAY_RING_FILL_RING(handle) \
    ((void *)((unsigned char *)(handle) + 0x4CU))
#define OPEN_CFW_UI_DISPLAY_RING_FILL_WRITE(ring, source, count) \
    open_cfw_test_ring_fill_write((ring), (source), (count))

#include "../../components/apollo_main/core_overlay/ui_display_ring_fill.c"
