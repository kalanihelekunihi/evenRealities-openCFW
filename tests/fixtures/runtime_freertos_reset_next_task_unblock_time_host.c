/*
 * MIT-licensed host harness for the shared G2 FreeRTOS next-unblock adapter.
 */

#include <stdint.h>

struct open_cfw_freertos_reset_unblock_list;

static struct open_cfw_freertos_reset_unblock_list *
open_cfw_test_reset_unblock_delayed_list_load(void);
static uint32_t open_cfw_test_reset_unblock_list_count_read(
    const struct open_cfw_freertos_reset_unblock_list *list
);
static uint32_t open_cfw_test_reset_unblock_head_value_read(
    const struct open_cfw_freertos_reset_unblock_list *list
);
static void open_cfw_test_reset_unblock_time_store(uint32_t value);

#define OPEN_CFW_FREERTOS_DELAYED_TASK_LIST_LOAD() \
    open_cfw_test_reset_unblock_delayed_list_load()
#define OPEN_CFW_FREERTOS_DELAYED_LIST_COUNT_READ(list) \
    open_cfw_test_reset_unblock_list_count_read((list))
#define OPEN_CFW_FREERTOS_DELAYED_LIST_HEAD_VALUE_READ(list) \
    open_cfw_test_reset_unblock_head_value_read((list))
#define OPEN_CFW_FREERTOS_NEXT_TASK_UNBLOCK_TIME_STORE(value) \
    open_cfw_test_reset_unblock_time_store((value))

#include \
    "../../components/shared/freertos/runtime_freertos_reset_next_task_unblock_time.c"

enum {
    OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_LIST_LOAD = 1,
    OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_COUNT_READ = 2,
    OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_HEAD_VALUE_READ = 3,
    OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_TIME_STORE = 4,
    OPEN_CFW_TEST_RESET_UNBLOCK_LIST_TOTAL = 3,
    OPEN_CFW_TEST_RESET_UNBLOCK_SNAPSHOT_TOTAL = 2,
    OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_CAPACITY = 6
};

struct open_cfw_test_reset_unblock_event {
    uint32_t kind;
    uint32_t subject;
    uint32_t value;
};

static struct open_cfw_freertos_reset_unblock_list
    open_cfw_test_reset_unblock_lists[
        OPEN_CFW_TEST_RESET_UNBLOCK_LIST_TOTAL
    ];
static struct open_cfw_freertos_reset_unblock_item
    open_cfw_test_reset_unblock_items[
        OPEN_CFW_TEST_RESET_UNBLOCK_LIST_TOTAL
    ];
static struct open_cfw_freertos_reset_unblock_list *
    open_cfw_test_reset_unblock_snapshots[
        OPEN_CFW_TEST_RESET_UNBLOCK_SNAPSHOT_TOTAL
    ];
static struct open_cfw_test_reset_unblock_event
    open_cfw_test_reset_unblock_events[
        OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_CAPACITY
    ];
static uint32_t open_cfw_test_reset_unblock_load_total;
static uint32_t open_cfw_test_reset_unblock_event_total;
static uint32_t open_cfw_test_reset_unblock_time_word;

static uint32_t open_cfw_test_reset_unblock_list_index(
    const struct open_cfw_freertos_reset_unblock_list *list
)
{
    uint32_t index;

    for (index = 0U;
         index < OPEN_CFW_TEST_RESET_UNBLOCK_LIST_TOTAL;
         ++index) {
        if (list == &open_cfw_test_reset_unblock_lists[index]) {
            return index;
        }
    }
    return UINT32_MAX;
}

static void open_cfw_test_reset_unblock_record(
    uint32_t kind,
    uint32_t subject,
    uint32_t value
)
{
    uint32_t index = open_cfw_test_reset_unblock_event_total;

    ++open_cfw_test_reset_unblock_event_total;
    if (index < OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_CAPACITY) {
        open_cfw_test_reset_unblock_events[index].kind = kind;
        open_cfw_test_reset_unblock_events[index].subject = subject;
        open_cfw_test_reset_unblock_events[index].value = value;
    }
}

static struct open_cfw_freertos_reset_unblock_list *
open_cfw_test_reset_unblock_delayed_list_load(void)
{
    uint32_t index = open_cfw_test_reset_unblock_load_total++;
    struct open_cfw_freertos_reset_unblock_list *list;

    if (index >= OPEN_CFW_TEST_RESET_UNBLOCK_SNAPSHOT_TOTAL) {
        index = OPEN_CFW_TEST_RESET_UNBLOCK_SNAPSHOT_TOTAL - 1U;
    }
    list = open_cfw_test_reset_unblock_snapshots[index];
    open_cfw_test_reset_unblock_record(
        OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_LIST_LOAD,
        open_cfw_test_reset_unblock_list_index(list),
        index
    );
    return list;
}

static uint32_t open_cfw_test_reset_unblock_list_count_read(
    const struct open_cfw_freertos_reset_unblock_list *list
)
{
    uint32_t value = list->item_count;

    open_cfw_test_reset_unblock_record(
        OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_COUNT_READ,
        open_cfw_test_reset_unblock_list_index(list),
        value
    );
    return value;
}

static uint32_t open_cfw_test_reset_unblock_head_value_read(
    const struct open_cfw_freertos_reset_unblock_list *list
)
{
    uint32_t value = list->end.next->item_value;

    open_cfw_test_reset_unblock_record(
        OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_HEAD_VALUE_READ,
        open_cfw_test_reset_unblock_list_index(list),
        value
    );
    return value;
}

static void open_cfw_test_reset_unblock_time_store(uint32_t value)
{
    open_cfw_test_reset_unblock_record(
        OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_TIME_STORE,
        UINT32_MAX,
        value
    );
    open_cfw_test_reset_unblock_time_word = value;
}

void open_cfw_test_reset_unblock_configure(
    uint32_t first_count,
    uint32_t first_head_value,
    uint32_t second_count,
    uint32_t second_head_value,
    uint32_t third_count,
    uint32_t third_head_value,
    uint32_t first_snapshot,
    uint32_t second_snapshot,
    uint32_t initial_time
)
{
    uint32_t counts[OPEN_CFW_TEST_RESET_UNBLOCK_LIST_TOTAL] = {
        first_count,
        second_count,
        third_count
    };
    uint32_t values[OPEN_CFW_TEST_RESET_UNBLOCK_LIST_TOTAL] = {
        first_head_value,
        second_head_value,
        third_head_value
    };
    uint32_t snapshots[OPEN_CFW_TEST_RESET_UNBLOCK_SNAPSHOT_TOTAL] = {
        first_snapshot % OPEN_CFW_TEST_RESET_UNBLOCK_LIST_TOTAL,
        second_snapshot % OPEN_CFW_TEST_RESET_UNBLOCK_LIST_TOTAL
    };
    uint32_t index;

    for (index = 0U;
         index < OPEN_CFW_TEST_RESET_UNBLOCK_LIST_TOTAL;
         ++index) {
        open_cfw_test_reset_unblock_lists[index].item_count = counts[index];
        open_cfw_test_reset_unblock_items[index].item_value = values[index];
        open_cfw_test_reset_unblock_lists[index].end.next =
            &open_cfw_test_reset_unblock_items[index];
    }
    for (index = 0U;
         index < OPEN_CFW_TEST_RESET_UNBLOCK_SNAPSHOT_TOTAL;
         ++index) {
        open_cfw_test_reset_unblock_snapshots[index] =
            &open_cfw_test_reset_unblock_lists[snapshots[index]];
    }
    for (index = 0U;
         index < OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_CAPACITY;
         ++index) {
        open_cfw_test_reset_unblock_events[index].kind = 0U;
        open_cfw_test_reset_unblock_events[index].subject = 0U;
        open_cfw_test_reset_unblock_events[index].value = 0U;
    }
    open_cfw_test_reset_unblock_load_total = 0U;
    open_cfw_test_reset_unblock_event_total = 0U;
    open_cfw_test_reset_unblock_time_word = initial_time;
}

void open_cfw_test_reset_unblock_invoke(void)
{
    open_cfw_freertos_task_reset_next_task_unblock_time();
}

uint32_t open_cfw_test_reset_unblock_time(void)
{
    return open_cfw_test_reset_unblock_time_word;
}

uint32_t open_cfw_test_reset_unblock_load_count(void)
{
    return open_cfw_test_reset_unblock_load_total;
}

uint32_t open_cfw_test_reset_unblock_event_count(void)
{
    return open_cfw_test_reset_unblock_event_total;
}

uint32_t open_cfw_test_reset_unblock_event_kind(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_CAPACITY) {
        return 0U;
    }
    return open_cfw_test_reset_unblock_events[index].kind;
}

uint32_t open_cfw_test_reset_unblock_event_subject(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_CAPACITY) {
        return 0U;
    }
    return open_cfw_test_reset_unblock_events[index].subject;
}

uint32_t open_cfw_test_reset_unblock_event_value(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_RESET_UNBLOCK_EVENT_CAPACITY) {
        return 0U;
    }
    return open_cfw_test_reset_unblock_events[index].value;
}
