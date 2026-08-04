unsigned int open_cfw_test_ring_drain_instance;
unsigned int open_cfw_test_ring_drain_interrupt_mask;
unsigned int open_cfw_test_ring_drain_enter_count;
unsigned int open_cfw_test_ring_drain_exit_count;
unsigned int open_cfw_test_ring_drain_exit_mask;
unsigned int open_cfw_test_ring_drain_full_after_writes;
unsigned int open_cfw_test_ring_drain_status_checks;
unsigned int open_cfw_test_ring_drain_status_instances[16];
unsigned char open_cfw_test_ring_drain_values[16];
unsigned int open_cfw_test_ring_drain_value_count;
unsigned int open_cfw_test_ring_drain_read_count;
void *open_cfw_test_ring_drain_read_ring;
unsigned int open_cfw_test_ring_drain_read_requested[16];
unsigned int open_cfw_test_ring_drain_direct_count;
unsigned int open_cfw_test_ring_drain_direct_error_call;
unsigned int open_cfw_test_ring_drain_direct_error;
void *open_cfw_test_ring_drain_direct_handle[16];
unsigned int open_cfw_test_ring_drain_direct_requested[16];
unsigned int open_cfw_test_ring_drain_direct_values[16];
unsigned int *open_cfw_test_ring_drain_direct_written[16];

void open_cfw_test_ring_drain_reset(void)
{
    unsigned int index;

    open_cfw_test_ring_drain_instance = 3U;
    open_cfw_test_ring_drain_interrupt_mask = 0U;
    open_cfw_test_ring_drain_enter_count = 0U;
    open_cfw_test_ring_drain_exit_count = 0U;
    open_cfw_test_ring_drain_exit_mask = 0xFFFFFFFFU;
    open_cfw_test_ring_drain_full_after_writes = 16U;
    open_cfw_test_ring_drain_status_checks = 0U;
    open_cfw_test_ring_drain_value_count = 0U;
    open_cfw_test_ring_drain_read_count = 0U;
    open_cfw_test_ring_drain_read_ring = (void *)0;
    open_cfw_test_ring_drain_direct_count = 0U;
    open_cfw_test_ring_drain_direct_error_call = 0xFFFFFFFFU;
    open_cfw_test_ring_drain_direct_error = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_ring_drain_status_instances[index] = 0U;
        open_cfw_test_ring_drain_values[index] = 0U;
        open_cfw_test_ring_drain_read_requested[index] = 0U;
        open_cfw_test_ring_drain_direct_handle[index] = (void *)0;
        open_cfw_test_ring_drain_direct_requested[index] = 0U;
        open_cfw_test_ring_drain_direct_values[index] = 0U;
        open_cfw_test_ring_drain_direct_written[index] =
            (unsigned int *)0;
    }
}

unsigned int open_cfw_test_ring_drain_critical_enter(void)
{
    ++open_cfw_test_ring_drain_enter_count;
    return open_cfw_test_ring_drain_interrupt_mask;
}

void open_cfw_test_ring_drain_critical_exit(unsigned int interrupt_mask)
{
    ++open_cfw_test_ring_drain_exit_count;
    open_cfw_test_ring_drain_exit_mask = interrupt_mask;
}

unsigned int open_cfw_test_ring_drain_fifo_full(unsigned int instance)
{
    unsigned int check = open_cfw_test_ring_drain_status_checks;

    open_cfw_test_ring_drain_status_instances[check] = instance;
    ++open_cfw_test_ring_drain_status_checks;
    return open_cfw_test_ring_drain_direct_count
        >= open_cfw_test_ring_drain_full_after_writes;
}

unsigned int open_cfw_test_ring_drain_read(
    void *ring,
    void *destination,
    unsigned int count
)
{
    unsigned int call = open_cfw_test_ring_drain_read_count;

    open_cfw_test_ring_drain_read_ring = ring;
    open_cfw_test_ring_drain_read_requested[call] = count;
    ++open_cfw_test_ring_drain_read_count;
    if (call >= open_cfw_test_ring_drain_value_count) {
        return 0U;
    }
    *(unsigned char *)destination = open_cfw_test_ring_drain_values[call];
    return 1U;
}

unsigned int open_cfw_test_ring_drain_direct_write(
    void *handle,
    const void *source,
    unsigned int count,
    unsigned int *written
)
{
    unsigned int call = open_cfw_test_ring_drain_direct_count;

    open_cfw_test_ring_drain_direct_handle[call] = handle;
    open_cfw_test_ring_drain_direct_requested[call] = count;
    open_cfw_test_ring_drain_direct_values[call] =
        *(const unsigned char *)source;
    open_cfw_test_ring_drain_direct_written[call] = written;
    ++open_cfw_test_ring_drain_direct_count;
    *written = count;
    if (call == open_cfw_test_ring_drain_direct_error_call) {
        return open_cfw_test_ring_drain_direct_error;
    }
    return 0U;
}

#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_CRITICAL_ENTER() \
    open_cfw_test_ring_drain_critical_enter()
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_test_ring_drain_critical_exit(interrupt_mask)
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_INSTANCE(handle) \
    ((void)(handle), open_cfw_test_ring_drain_instance)
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_FIFO_FULL(instance) \
    open_cfw_test_ring_drain_fifo_full(instance)
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_RING(handle) \
    ((void *)((unsigned char *)(handle) + 0x34U))
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_READ(ring, destination, count) \
    open_cfw_test_ring_drain_read((ring), (destination), (count))
#define OPEN_CFW_UI_DISPLAY_RING_DRAIN_DIRECT_WRITE( \
    handle, \
    source, \
    count, \
    written \
) \
    open_cfw_test_ring_drain_direct_write( \
        (handle), \
        (source), \
        (count), \
        (written) \
    )

#include "../../components/apollo_main/core_overlay/ui_display_ring_drain.c"
