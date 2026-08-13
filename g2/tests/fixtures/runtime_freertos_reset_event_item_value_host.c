/*
 * MIT-licensed host harness for the shared G2 FreeRTOS event-item reset leaf.
 */

#include <stdint.h>

struct open_cfw_test_event_tcb;

static struct open_cfw_test_event_tcb
    *open_cfw_test_current_tcb_snapshots[3];
static volatile uint32_t open_cfw_test_current_tcb_load_count;

static struct open_cfw_test_event_tcb
    *open_cfw_test_current_tcb_load(void)
{
    uint32_t index = open_cfw_test_current_tcb_load_count++;

    if (index >= 3U) {
        index = 2U;
    }
    return open_cfw_test_current_tcb_snapshots[index];
}

#define OPEN_CFW_FREERTOS_CURRENT_TCB_LOAD() \
    ((struct open_cfw_freertos_event_tcb *) \
        open_cfw_test_current_tcb_load())

#include \
    "../../components/shared/freertos/runtime_freertos_reset_event_item_value.c"

struct open_cfw_test_event_tcb {
    uint8_t before_event_item_value[0x18];
    volatile uint32_t event_item_value;
    uint8_t before_priority[0x10];
    volatile uint32_t priority;
};

static struct open_cfw_test_event_tcb open_cfw_test_tcbs[3];

void open_cfw_test_freertos_reset_event_item_configure(
    uint32_t first_event,
    uint32_t first_priority,
    uint32_t second_event,
    uint32_t second_priority,
    uint32_t third_event,
    uint32_t third_priority,
    uint32_t first_snapshot,
    uint32_t second_snapshot,
    uint32_t third_snapshot)
{
    uint32_t snapshots[3] = {
        first_snapshot % 3U,
        second_snapshot % 3U,
        third_snapshot % 3U
    };
    uint32_t events[3] = {
        first_event,
        second_event,
        third_event
    };
    uint32_t priorities[3] = {
        first_priority,
        second_priority,
        third_priority
    };
    uint32_t index;

    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_tcbs[index].event_item_value = events[index];
        open_cfw_test_tcbs[index].priority = priorities[index];
        open_cfw_test_current_tcb_snapshots[index] =
            &open_cfw_test_tcbs[snapshots[index]];
    }
    open_cfw_test_current_tcb_load_count = 0U;
}

uint32_t open_cfw_test_freertos_reset_event_item_invoke(void)
{
    return open_cfw_freertos_task_reset_event_item_value();
}

uint32_t open_cfw_test_freertos_reset_event_item_event(uint32_t index)
{
    return open_cfw_test_tcbs[index % 3U].event_item_value;
}

uint32_t open_cfw_test_freertos_reset_event_item_priority(uint32_t index)
{
    return open_cfw_test_tcbs[index % 3U].priority;
}

uint32_t open_cfw_test_freertos_reset_event_item_loads(void)
{
    return open_cfw_test_current_tcb_load_count;
}
