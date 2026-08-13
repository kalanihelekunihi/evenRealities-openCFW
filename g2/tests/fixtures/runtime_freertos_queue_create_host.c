/*
 * SPDX-License-Identifier: MIT
 *
 * Host oracle for the bounded FreeRTOS queue-creation source boundary.
 */

#include <setjmp.h>
#include <stddef.h>
#include <string.h>

struct open_cfw_queue_create_control;

static void open_cfw_test_queue_create_assert(int condition);
static int open_cfw_test_queue_create_reset_call(
    struct open_cfw_queue_create_control *queue,
    int new_queue
);
static void *open_cfw_test_queue_create_malloc(unsigned int size);
static int open_cfw_test_queue_create_send(
    struct open_cfw_queue_create_control *queue,
    const void *item,
    unsigned int ticks,
    int position
);

#define OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT(condition) \
    open_cfw_test_queue_create_assert((condition))
#define OPEN_CFW_FREERTOS_QUEUE_CREATE_RESET(queue, new_queue) \
    open_cfw_test_queue_create_reset_call((queue), (new_queue))
#define OPEN_CFW_FREERTOS_QUEUE_CREATE_MALLOC(size) \
    open_cfw_test_queue_create_malloc((size))
#define OPEN_CFW_FREERTOS_QUEUE_CREATE_SEND(queue, item, ticks, position) \
    open_cfw_test_queue_create_send((queue), (item), (ticks), (position))

#include "../../components/apollo_main/core_overlay/runtime_freertos_queue_create.c"

static union {
    void *alignment;
    unsigned char bytes[512];
} open_cfw_test_queue_create_allocation;
static struct open_cfw_queue_create_control
    open_cfw_test_queue_create_static_queue;
static unsigned char open_cfw_test_queue_create_storage[256];
static jmp_buf open_cfw_test_queue_create_assert_jump;
static unsigned int open_cfw_test_queue_create_assert_armed;

unsigned int open_cfw_test_queue_create_assert_count;
unsigned int open_cfw_test_queue_create_malloc_success;
unsigned int open_cfw_test_queue_create_malloc_size;
unsigned int open_cfw_test_queue_create_reset_count;
unsigned int open_cfw_test_queue_create_reset_new_queue;
unsigned int open_cfw_test_queue_create_send_count;
unsigned int open_cfw_test_queue_create_send_ticks;
int open_cfw_test_queue_create_send_position;

static void open_cfw_test_queue_create_assert(int condition)
{
    if (condition != 0) {
        return;
    }
    open_cfw_test_queue_create_assert_count++;
    if (open_cfw_test_queue_create_assert_armed != 0U) {
        longjmp(open_cfw_test_queue_create_assert_jump, 1);
    }
}

static int open_cfw_test_queue_create_reset_call(
    struct open_cfw_queue_create_control *queue,
    int new_queue
)
{
    open_cfw_test_queue_create_reset_count++;
    open_cfw_test_queue_create_reset_new_queue = (unsigned int)new_queue;
    queue->messages_waiting = 0U;
    queue->receive_lock = (signed char)-1;
    queue->transmit_lock = (signed char)-1;
    return 1;
}

static void *open_cfw_test_queue_create_malloc(unsigned int size)
{
    open_cfw_test_queue_create_malloc_size = size;
    if (open_cfw_test_queue_create_malloc_success == 0U) {
        return 0;
    }
    return open_cfw_test_queue_create_allocation.bytes;
}

static int open_cfw_test_queue_create_send(
    struct open_cfw_queue_create_control *queue,
    const void *item,
    unsigned int ticks,
    int position
)
{
    (void)item;
    open_cfw_test_queue_create_send_count++;
    open_cfw_test_queue_create_send_ticks = ticks;
    open_cfw_test_queue_create_send_position = position;
    queue->messages_waiting++;
    return 1;
}

void open_cfw_test_queue_create_host_reset(void)
{
    memset(
        open_cfw_test_queue_create_allocation.bytes,
        0xA5,
        sizeof(open_cfw_test_queue_create_allocation.bytes)
    );
    memset(
        &open_cfw_test_queue_create_static_queue,
        0xA5,
        sizeof(open_cfw_test_queue_create_static_queue)
    );
    memset(
        open_cfw_test_queue_create_storage,
        0,
        sizeof(open_cfw_test_queue_create_storage)
    );
    open_cfw_test_queue_create_assert_count = 0U;
    open_cfw_test_queue_create_malloc_success = 1U;
    open_cfw_test_queue_create_malloc_size = 0U;
    open_cfw_test_queue_create_reset_count = 0U;
    open_cfw_test_queue_create_reset_new_queue = 0U;
    open_cfw_test_queue_create_send_count = 0U;
    open_cfw_test_queue_create_send_ticks = 0U;
    open_cfw_test_queue_create_send_position = -1;
    open_cfw_test_queue_create_assert_armed = 0U;
}

void *open_cfw_test_queue_create_static_pointer(void)
{
    return &open_cfw_test_queue_create_static_queue;
}

void *open_cfw_test_queue_create_storage_pointer(void)
{
    return open_cfw_test_queue_create_storage;
}

void *open_cfw_test_queue_create_allocation_pointer(void)
{
    return open_cfw_test_queue_create_allocation.bytes;
}

unsigned int open_cfw_test_queue_create_control_size(void)
{
    return (unsigned int)sizeof(struct open_cfw_queue_create_control);
}

unsigned long open_cfw_test_queue_create_head(void *pointer)
{
    struct open_cfw_queue_create_control *queue =
        (struct open_cfw_queue_create_control *)pointer;
    return (unsigned long)queue->head;
}

unsigned int open_cfw_test_queue_create_length(void *pointer)
{
    struct open_cfw_queue_create_control *queue =
        (struct open_cfw_queue_create_control *)pointer;
    return queue->length;
}

unsigned int open_cfw_test_queue_create_item_size(void *pointer)
{
    struct open_cfw_queue_create_control *queue =
        (struct open_cfw_queue_create_control *)pointer;
    return queue->item_size;
}

unsigned int open_cfw_test_queue_create_static_marker(void *pointer)
{
    struct open_cfw_queue_create_control *queue =
        (struct open_cfw_queue_create_control *)pointer;
    return queue->statically_allocated;
}

unsigned int open_cfw_test_queue_create_type(void *pointer)
{
    struct open_cfw_queue_create_control *queue =
        (struct open_cfw_queue_create_control *)pointer;
    return queue->queue_type;
}

unsigned int open_cfw_test_queue_create_messages(void *pointer)
{
    struct open_cfw_queue_create_control *queue =
        (struct open_cfw_queue_create_control *)pointer;
    return queue->messages_waiting;
}

unsigned long open_cfw_test_queue_create_mutex_holder(void *pointer)
{
    struct open_cfw_queue_create_control *queue =
        (struct open_cfw_queue_create_control *)pointer;
    return (unsigned long)queue->value.semaphore.mutex_holder;
}

unsigned int open_cfw_test_queue_create_recursive_count(void *pointer)
{
    struct open_cfw_queue_create_control *queue =
        (struct open_cfw_queue_create_control *)pointer;
    return queue->value.semaphore.recursive_call_count;
}

int open_cfw_test_queue_create_dynamic_asserting(
    unsigned int length,
    unsigned int item_size
)
{
    int jumped = setjmp(open_cfw_test_queue_create_assert_jump);
    if (jumped != 0) {
        open_cfw_test_queue_create_assert_armed = 0U;
        return 1;
    }
    open_cfw_test_queue_create_assert_armed = 1U;
    (void)open_cfw_freertos_queue_generic_create(
        length,
        item_size,
        0U
    );
    open_cfw_test_queue_create_assert_armed = 0U;
    return 0;
}

int open_cfw_test_queue_create_static_asserting(
    unsigned int length,
    unsigned int item_size,
    int provide_storage,
    int provide_queue
)
{
    int jumped = setjmp(open_cfw_test_queue_create_assert_jump);
    if (jumped != 0) {
        open_cfw_test_queue_create_assert_armed = 0U;
        return 1;
    }
    open_cfw_test_queue_create_assert_armed = 1U;
    (void)open_cfw_freertos_queue_generic_create_static(
        length,
        item_size,
        provide_storage != 0 ? open_cfw_test_queue_create_storage : 0,
        provide_queue != 0 ? &open_cfw_test_queue_create_static_queue : 0,
        0U
    );
    open_cfw_test_queue_create_assert_armed = 0U;
    return 0;
}
