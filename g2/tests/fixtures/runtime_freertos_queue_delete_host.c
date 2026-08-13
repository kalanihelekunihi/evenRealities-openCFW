#include <stddef.h>
#include <stdint.h>
#include <string.h>

static unsigned int open_cfw_test_queue_delete_assert_calls;
static unsigned int open_cfw_test_queue_delete_mask_calls;
static unsigned int open_cfw_test_queue_delete_free_calls;
static void *open_cfw_test_queue_delete_last_free;

static void open_cfw_test_queue_delete_record_assert(void)
{
    open_cfw_test_queue_delete_assert_calls++;
    open_cfw_test_queue_delete_mask_calls++;
}

static void open_cfw_test_queue_delete_record_free(void *allocation)
{
    open_cfw_test_queue_delete_free_calls++;
    open_cfw_test_queue_delete_last_free = allocation;
}

#define OPEN_CFW_FREERTOS_QUEUE_DELETE_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            open_cfw_test_queue_delete_record_assert(); \
            return; \
        } \
    } while (0)
#define OPEN_CFW_FREERTOS_QUEUE_DELETE_FREE(allocation) \
    open_cfw_test_queue_delete_record_free((allocation))
#include "../../components/apollo_main/core_overlay/runtime_freertos_queue_delete.c"

struct open_cfw_test_queue_delete_result
{
    unsigned int assert_calls;
    unsigned int mask_calls;
    unsigned int free_calls;
    uintptr_t freed_pointer;
};

static open_cfw_queue_delete_control open_cfw_test_queue_delete_queue;

void open_cfw_test_queue_delete_reset(void)
{
    open_cfw_test_queue_delete_assert_calls = 0U;
    open_cfw_test_queue_delete_mask_calls = 0U;
    open_cfw_test_queue_delete_free_calls = 0U;
    open_cfw_test_queue_delete_last_free = NULL;
    memset(
        &open_cfw_test_queue_delete_queue,
        0xA5,
        sizeof(open_cfw_test_queue_delete_queue));
}

uintptr_t open_cfw_test_queue_delete_queue_pointer(void)
{
    return (uintptr_t)&open_cfw_test_queue_delete_queue;
}

unsigned int open_cfw_test_queue_delete_queue_size(void)
{
    return (unsigned int)sizeof(open_cfw_test_queue_delete_queue);
}

unsigned int open_cfw_test_queue_delete_marker_offset(void)
{
    return (unsigned int)offsetof(
        open_cfw_queue_delete_control,
        ucStaticallyAllocated);
}

void open_cfw_test_queue_delete_call(
    int use_null_queue,
    unsigned int allocation_marker,
    struct open_cfw_test_queue_delete_result *result)
{
    open_cfw_queue_delete_control *queue =
        use_null_queue ? NULL : &open_cfw_test_queue_delete_queue;

    open_cfw_test_queue_delete_reset();
    if (queue != NULL)
    {
        queue->ucStaticallyAllocated =
            (open_cfw_queue_delete_uint8)allocation_marker;
    }

    open_cfw_freertos_queue_delete(queue);

    result->assert_calls = open_cfw_test_queue_delete_assert_calls;
    result->mask_calls = open_cfw_test_queue_delete_mask_calls;
    result->free_calls = open_cfw_test_queue_delete_free_calls;
    result->freed_pointer =
        (uintptr_t)open_cfw_test_queue_delete_last_free;
}

void open_cfw_test_queue_delete_oracle(
    int use_null_queue,
    unsigned int allocation_marker,
    struct open_cfw_test_queue_delete_result *result)
{
    open_cfw_queue_delete_control *queue =
        use_null_queue ? NULL : &open_cfw_test_queue_delete_queue;

    open_cfw_test_queue_delete_reset();
    if (queue == NULL)
    {
        open_cfw_test_queue_delete_record_assert();
    }
    else
    {
        queue->ucStaticallyAllocated =
            (open_cfw_queue_delete_uint8)allocation_marker;
        if (queue->ucStaticallyAllocated == 0U)
        {
            open_cfw_test_queue_delete_record_free(queue);
        }
    }

    result->assert_calls = open_cfw_test_queue_delete_assert_calls;
    result->mask_calls = open_cfw_test_queue_delete_mask_calls;
    result->free_calls = open_cfw_test_queue_delete_free_calls;
    result->freed_pointer =
        (uintptr_t)open_cfw_test_queue_delete_last_free;
}
