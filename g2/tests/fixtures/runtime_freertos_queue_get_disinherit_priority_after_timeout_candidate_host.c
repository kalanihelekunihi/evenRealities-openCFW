#include <stddef.h>
#include <stdint.h>
#include <string.h>

struct open_cfw_test_disinherit_raw_queue {
    union {
        max_align_t alignment;
        unsigned char bytes[0x40];
    } storage;
};

struct open_cfw_test_disinherit_item {
    uint32_t item_value;
};

static uint32_t open_cfw_test_disinherit_list_length(const void *queue)
{
    uint32_t value;

    memcpy(&value, (const unsigned char *)queue + 0x24, sizeof(value));
    return value;
}

static uint32_t open_cfw_test_disinherit_head_item_value(const void *queue)
{
    const struct open_cfw_test_disinherit_item *item;

    memcpy(&item, (const unsigned char *)queue + 0x30, sizeof(item));
    return item->item_value;
}

#define OPEN_CFW_FREERTOS_DISINHERIT_LIST_LENGTH(queue) \
    open_cfw_test_disinherit_list_length((queue))
#define OPEN_CFW_FREERTOS_DISINHERIT_HEAD_ITEM_VALUE(queue) \
    open_cfw_test_disinherit_head_item_value((queue))
#include "../../components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.c"

typedef uint32_t UBaseType_t;

typedef struct ListItem {
    UBaseType_t xItemValue;
} ListItem_t;

typedef struct List {
    UBaseType_t uxNumberOfItems;
    ListItem_t *head;
} List_t;

typedef struct Queue {
    List_t xTasksWaitingToReceive;
} Queue_t;

#define configMAX_PRIORITIES 56U
#define tskIDLE_PRIORITY 0U
#define listCURRENT_LIST_LENGTH(list) ((list)->uxNumberOfItems)
#define listGET_ITEM_VALUE_OF_HEAD_ENTRY(list) ((list)->head->xItemValue)

/* Separately named copy of the pristine V10.5.1 operation. */
static UBaseType_t open_cfw_test_disinherit_upstream_oracle(
    const Queue_t * const pxQueue
)
{
    UBaseType_t uxHighestPriorityOfWaitingTasks;

    if (listCURRENT_LIST_LENGTH(&(pxQueue->xTasksWaitingToReceive)) > 0U) {
        uxHighestPriorityOfWaitingTasks =
            (UBaseType_t)configMAX_PRIORITIES -
            (UBaseType_t)listGET_ITEM_VALUE_OF_HEAD_ENTRY(
                &(pxQueue->xTasksWaitingToReceive)
            );
    } else {
        uxHighestPriorityOfWaitingTasks = tskIDLE_PRIORITY;
    }

    return uxHighestPriorityOfWaitingTasks;
}

uint32_t open_cfw_test_disinherit_candidate(
    uint32_t number_of_items,
    uint32_t head_item_value
)
{
    struct open_cfw_test_disinherit_raw_queue queue;
    struct open_cfw_test_disinherit_item item = {head_item_value};
    const struct open_cfw_test_disinherit_item *item_pointer = &item;

    memset(&queue, 0xA7, sizeof(queue));
    memcpy(
        queue.storage.bytes + 0x24,
        &number_of_items,
        sizeof(number_of_items)
    );
    if (number_of_items > 0U) {
        memcpy(
            queue.storage.bytes + 0x30,
            &item_pointer,
            sizeof(item_pointer)
        );
    } else {
        memset(queue.storage.bytes + 0x30, 0, sizeof(item_pointer));
    }

    return open_cfw_freertos_queue_get_disinherit_priority_after_timeout(
        queue.storage.bytes
    );
}

uint32_t open_cfw_test_disinherit_oracle(
    uint32_t number_of_items,
    uint32_t head_item_value
)
{
    ListItem_t item = {head_item_value};
    Queue_t queue = {{number_of_items, number_of_items > 0U ? &item : NULL}};

    return open_cfw_test_disinherit_upstream_oracle(&queue);
}
