/*
 * MIT-licensed host harness for the shared G2 FreeRTOS suspend-all adapter.
 */

#include <stdint.h>

enum {
    OPEN_CFW_TEST_SUSPEND_ALL_EVENT_SOFTWARE_BARRIER = 1,
    OPEN_CFW_TEST_SUSPEND_ALL_EVENT_DEPTH_READ = 2,
    OPEN_CFW_TEST_SUSPEND_ALL_EVENT_DEPTH_WRITE = 3,
    OPEN_CFW_TEST_SUSPEND_ALL_EVENT_MEMORY_BARRIER = 4,
    OPEN_CFW_TEST_SUSPEND_ALL_EVENT_CAPACITY = 4
};

struct open_cfw_test_suspend_all_event {
    uint32_t kind;
    uint32_t value;
};

static uint32_t open_cfw_test_suspend_all_depth;
static struct open_cfw_test_suspend_all_event
    open_cfw_test_suspend_all_events[
        OPEN_CFW_TEST_SUSPEND_ALL_EVENT_CAPACITY
    ];
static uint32_t open_cfw_test_suspend_all_event_total;
static uint32_t open_cfw_test_suspend_all_depth_reads;
static uint32_t open_cfw_test_suspend_all_depth_writes;
static uint32_t open_cfw_test_suspend_all_software_barriers;
static uint32_t open_cfw_test_suspend_all_memory_barriers;

static void open_cfw_test_suspend_all_record(
    uint32_t kind,
    uint32_t value
)
{
    uint32_t index = open_cfw_test_suspend_all_event_total;

    ++open_cfw_test_suspend_all_event_total;
    if (index < OPEN_CFW_TEST_SUSPEND_ALL_EVENT_CAPACITY) {
        open_cfw_test_suspend_all_events[index].kind = kind;
        open_cfw_test_suspend_all_events[index].value = value;
    }
}

static void open_cfw_test_suspend_all_software_barrier(void)
{
    ++open_cfw_test_suspend_all_software_barriers;
    open_cfw_test_suspend_all_record(
        OPEN_CFW_TEST_SUSPEND_ALL_EVENT_SOFTWARE_BARRIER,
        open_cfw_test_suspend_all_depth
    );
}

static uint32_t open_cfw_test_suspend_all_depth_read(void)
{
    ++open_cfw_test_suspend_all_depth_reads;
    open_cfw_test_suspend_all_record(
        OPEN_CFW_TEST_SUSPEND_ALL_EVENT_DEPTH_READ,
        open_cfw_test_suspend_all_depth
    );
    return open_cfw_test_suspend_all_depth;
}

static void open_cfw_test_suspend_all_depth_write(uint32_t value)
{
    ++open_cfw_test_suspend_all_depth_writes;
    open_cfw_test_suspend_all_record(
        OPEN_CFW_TEST_SUSPEND_ALL_EVENT_DEPTH_WRITE,
        value
    );
    open_cfw_test_suspend_all_depth = value;
}

static void open_cfw_test_suspend_all_memory_barrier(void)
{
    ++open_cfw_test_suspend_all_memory_barriers;
    open_cfw_test_suspend_all_record(
        OPEN_CFW_TEST_SUSPEND_ALL_EVENT_MEMORY_BARRIER,
        open_cfw_test_suspend_all_depth
    );
}

#define OPEN_CFW_FREERTOS_SUSPEND_ALL_SOFTWARE_BARRIER() \
    open_cfw_test_suspend_all_software_barrier()
#define OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_READ() \
    open_cfw_test_suspend_all_depth_read()
#define OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_WRITE(value) \
    open_cfw_test_suspend_all_depth_write((value))
#define OPEN_CFW_FREERTOS_SUSPEND_ALL_MEMORY_BARRIER() \
    open_cfw_test_suspend_all_memory_barrier()

#include \
    "../../components/shared/freertos/runtime_freertos_suspend_all.c"

void open_cfw_test_suspend_all_reset(uint32_t depth)
{
    uint32_t index;

    open_cfw_test_suspend_all_depth = depth;
    open_cfw_test_suspend_all_event_total = 0U;
    open_cfw_test_suspend_all_depth_reads = 0U;
    open_cfw_test_suspend_all_depth_writes = 0U;
    open_cfw_test_suspend_all_software_barriers = 0U;
    open_cfw_test_suspend_all_memory_barriers = 0U;
    for (index = 0U;
         index < OPEN_CFW_TEST_SUSPEND_ALL_EVENT_CAPACITY;
         ++index) {
        open_cfw_test_suspend_all_events[index].kind = 0U;
        open_cfw_test_suspend_all_events[index].value = 0U;
    }
}

void open_cfw_test_suspend_all_invoke(void)
{
    open_cfw_freertos_task_suspend_all();
}

uint32_t open_cfw_test_suspend_all_depth_get(void)
{
    return open_cfw_test_suspend_all_depth;
}

uint32_t open_cfw_test_suspend_all_event_count(void)
{
    return open_cfw_test_suspend_all_event_total;
}

uint32_t open_cfw_test_suspend_all_event_kind(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_SUSPEND_ALL_EVENT_CAPACITY) {
        return 0U;
    }
    return open_cfw_test_suspend_all_events[index].kind;
}

uint32_t open_cfw_test_suspend_all_event_value(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_SUSPEND_ALL_EVENT_CAPACITY) {
        return 0U;
    }
    return open_cfw_test_suspend_all_events[index].value;
}

uint32_t open_cfw_test_suspend_all_depth_read_count(void)
{
    return open_cfw_test_suspend_all_depth_reads;
}

uint32_t open_cfw_test_suspend_all_depth_write_count(void)
{
    return open_cfw_test_suspend_all_depth_writes;
}

uint32_t open_cfw_test_suspend_all_software_barrier_count(void)
{
    return open_cfw_test_suspend_all_software_barriers;
}

uint32_t open_cfw_test_suspend_all_memory_barrier_count(void)
{
    return open_cfw_test_suspend_all_memory_barriers;
}
