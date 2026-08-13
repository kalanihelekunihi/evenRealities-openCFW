/*
 * SPDX-License-Identifier: MIT
 *
 * Host oracle for the source-owned FreeRTOS queue public-function boundary.
 */

#include <setjmp.h>
#include <stddef.h>
#include <string.h>

struct open_cfw_queue_control;
struct open_cfw_queue_list;
struct open_cfw_queue_timeout;

static void open_cfw_test_queue_assert(int condition);
static struct open_cfw_queue_control *
open_cfw_test_queue_generic_create(
    unsigned int length,
    unsigned int item_size,
    unsigned char queue_type
);
static void open_cfw_test_queue_initialise_mutex(
    struct open_cfw_queue_control *queue
);
static int open_cfw_test_queue_scheduler_state(void);
static void *open_cfw_test_queue_current_task(void);
static void open_cfw_test_queue_enter_critical(void);
static void open_cfw_test_queue_exit_critical(void);
static int open_cfw_test_queue_copy_data(
    struct open_cfw_queue_control *queue,
    const void *item,
    int position
);
static int open_cfw_test_queue_remove_event(
    struct open_cfw_queue_list *list
);
static void open_cfw_test_queue_yield(void);
static void open_cfw_test_queue_set_timeout(
    struct open_cfw_queue_timeout *timeout
);
static void open_cfw_test_queue_suspend_all(void);
static int open_cfw_test_queue_check_timeout(
    struct open_cfw_queue_timeout *timeout,
    unsigned int *ticks_to_wait
);
static int open_cfw_test_queue_is_full(
    const struct open_cfw_queue_control *queue
);
static void open_cfw_test_queue_place_on_event(
    struct open_cfw_queue_list *list,
    unsigned int ticks_to_wait
);
static void open_cfw_test_queue_unlock(
    struct open_cfw_queue_control *queue
);
static int open_cfw_test_queue_resume_all(void);
static int open_cfw_test_queue_is_empty(
    const struct open_cfw_queue_control *queue
);
static void *open_cfw_test_queue_increment_mutex_held(void);
static int open_cfw_test_queue_priority_inherit(void *mutex_holder);
static unsigned int open_cfw_test_queue_disinherit_priority(
    const struct open_cfw_queue_control *queue
);
static void open_cfw_test_queue_disinherit_after_timeout(
    void *mutex_holder,
    unsigned int highest_waiting_priority
);

#define OPEN_CFW_FREERTOS_QUEUE_ASSERT(condition) \
    open_cfw_test_queue_assert((condition))
#define OPEN_CFW_FREERTOS_QUEUE_GENERIC_CREATE(length, item_size, type) \
    open_cfw_test_queue_generic_create((length), (item_size), (type))
#define OPEN_CFW_FREERTOS_QUEUE_INITIALISE_MUTEX(queue) \
    open_cfw_test_queue_initialise_mutex((queue))
#define OPEN_CFW_FREERTOS_QUEUE_SCHEDULER_STATE() \
    open_cfw_test_queue_scheduler_state()
#define OPEN_CFW_FREERTOS_QUEUE_CURRENT_TASK() \
    open_cfw_test_queue_current_task()
#define OPEN_CFW_FREERTOS_QUEUE_ENTER_CRITICAL() \
    open_cfw_test_queue_enter_critical()
#define OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL() \
    open_cfw_test_queue_exit_critical()
#define OPEN_CFW_FREERTOS_QUEUE_COPY_DATA(queue, item, position) \
    open_cfw_test_queue_copy_data((queue), (item), (position))
#define OPEN_CFW_FREERTOS_QUEUE_REMOVE_EVENT(list) \
    open_cfw_test_queue_remove_event((list))
#define OPEN_CFW_FREERTOS_QUEUE_YIELD() open_cfw_test_queue_yield()
#define OPEN_CFW_FREERTOS_QUEUE_SET_TIMEOUT(timeout) \
    open_cfw_test_queue_set_timeout((timeout))
#define OPEN_CFW_FREERTOS_QUEUE_SUSPEND_ALL() \
    open_cfw_test_queue_suspend_all()
#define OPEN_CFW_FREERTOS_QUEUE_CHECK_TIMEOUT(timeout, ticks) \
    open_cfw_test_queue_check_timeout((timeout), (ticks))
#define OPEN_CFW_FREERTOS_QUEUE_IS_FULL(queue) \
    open_cfw_test_queue_is_full((queue))
#define OPEN_CFW_FREERTOS_QUEUE_PLACE_ON_EVENT(list, ticks) \
    open_cfw_test_queue_place_on_event((list), (ticks))
#define OPEN_CFW_FREERTOS_QUEUE_UNLOCK(queue) \
    open_cfw_test_queue_unlock((queue))
#define OPEN_CFW_FREERTOS_QUEUE_RESUME_ALL() \
    open_cfw_test_queue_resume_all()
#define OPEN_CFW_FREERTOS_QUEUE_IS_EMPTY(queue) \
    open_cfw_test_queue_is_empty((queue))
#define OPEN_CFW_FREERTOS_QUEUE_INCREMENT_MUTEX_HELD() \
    open_cfw_test_queue_increment_mutex_held()
#define OPEN_CFW_FREERTOS_QUEUE_PRIORITY_INHERIT(holder) \
    open_cfw_test_queue_priority_inherit((holder))
#define OPEN_CFW_FREERTOS_QUEUE_DISINHERIT_PRIORITY(queue) \
    open_cfw_test_queue_disinherit_priority((queue))
#define OPEN_CFW_FREERTOS_QUEUE_DISINHERIT_AFTER_TIMEOUT(holder, priority) \
    open_cfw_test_queue_disinherit_after_timeout((holder), (priority))

#define OPEN_CFW_FREERTOS_QUEUE_INCLUDE_LEGACY_SEMAPHORE_TAKE 1
#include "../../components/apollo_main/core_overlay/runtime_freertos_queue.c"

enum {
    OPEN_CFW_TEST_QUEUE_EVENT_GENERIC_CREATE = 1,
    OPEN_CFW_TEST_QUEUE_EVENT_INITIALISE_MUTEX = 2,
    OPEN_CFW_TEST_QUEUE_EVENT_ENTER_CRITICAL = 3,
    OPEN_CFW_TEST_QUEUE_EVENT_EXIT_CRITICAL = 4,
    OPEN_CFW_TEST_QUEUE_EVENT_COPY_DATA = 5,
    OPEN_CFW_TEST_QUEUE_EVENT_REMOVE_EVENT = 6,
    OPEN_CFW_TEST_QUEUE_EVENT_YIELD = 7,
    OPEN_CFW_TEST_QUEUE_EVENT_SET_TIMEOUT = 8,
    OPEN_CFW_TEST_QUEUE_EVENT_SUSPEND_ALL = 9,
    OPEN_CFW_TEST_QUEUE_EVENT_CHECK_TIMEOUT = 10,
    OPEN_CFW_TEST_QUEUE_EVENT_PLACE_ON_EVENT = 11,
    OPEN_CFW_TEST_QUEUE_EVENT_UNLOCK = 12,
    OPEN_CFW_TEST_QUEUE_EVENT_RESUME_ALL = 13,
    OPEN_CFW_TEST_QUEUE_EVENT_INCREMENT_MUTEX_HELD = 14,
    OPEN_CFW_TEST_QUEUE_EVENT_PRIORITY_INHERIT = 15,
    OPEN_CFW_TEST_QUEUE_EVENT_DISINHERIT_PRIORITY = 16,
    OPEN_CFW_TEST_QUEUE_EVENT_DISINHERIT_AFTER_TIMEOUT = 17,
    OPEN_CFW_TEST_QUEUE_EVENT_ASSERT = 18,
    OPEN_CFW_TEST_QUEUE_EVENT_CURRENT_TASK = 19,
    OPEN_CFW_TEST_QUEUE_EVENT_CAPACITY = 128
};

unsigned int open_cfw_test_queue_event_count;
unsigned int
open_cfw_test_queue_events[OPEN_CFW_TEST_QUEUE_EVENT_CAPACITY];
unsigned int open_cfw_test_queue_arguments0[
    OPEN_CFW_TEST_QUEUE_EVENT_CAPACITY
];
unsigned int open_cfw_test_queue_arguments1[
    OPEN_CFW_TEST_QUEUE_EVENT_CAPACITY
];

unsigned int open_cfw_test_queue_scheduler_state_value;
unsigned int open_cfw_test_queue_generic_create_success;
unsigned int open_cfw_test_queue_copy_yield;
unsigned int open_cfw_test_queue_remove_event_result;
unsigned int open_cfw_test_queue_resume_all_result;
unsigned int open_cfw_test_queue_check_timeout_result;
unsigned int open_cfw_test_queue_check_timeout_mutation;
unsigned int open_cfw_test_queue_check_timeout_result_after_first;
unsigned int open_cfw_test_queue_check_timeout_mutation_after_first;
unsigned int open_cfw_test_queue_check_timeout_calls;
unsigned int open_cfw_test_queue_priority_inherit_result;
unsigned int open_cfw_test_queue_highest_waiting_priority;
unsigned long open_cfw_test_queue_current_task_value;
unsigned long open_cfw_test_queue_mutex_holder_value;
unsigned long open_cfw_test_queue_disinherit_holder;
unsigned int open_cfw_test_queue_disinherit_priority_value;
unsigned int open_cfw_test_queue_assert_count;

static struct open_cfw_queue_control open_cfw_test_queue_control;
static unsigned char open_cfw_test_queue_storage[256];
static jmp_buf open_cfw_test_queue_assert_jump;
static unsigned int open_cfw_test_queue_assert_armed;

static void open_cfw_test_queue_log(
    unsigned int event,
    unsigned int argument0,
    unsigned int argument1
)
{
    unsigned int index = open_cfw_test_queue_event_count;

    if (index < OPEN_CFW_TEST_QUEUE_EVENT_CAPACITY) {
        open_cfw_test_queue_events[index] = event;
        open_cfw_test_queue_arguments0[index] = argument0;
        open_cfw_test_queue_arguments1[index] = argument1;
    }
    open_cfw_test_queue_event_count = index + 1U;
}

static void open_cfw_test_queue_assert(int condition)
{
    if (condition != 0) {
        return;
    }
    open_cfw_test_queue_assert_count++;
    open_cfw_test_queue_log(OPEN_CFW_TEST_QUEUE_EVENT_ASSERT, 0U, 0U);
    if (open_cfw_test_queue_assert_armed != 0U) {
        longjmp(open_cfw_test_queue_assert_jump, 1);
    }
    __builtin_trap();
}

static struct open_cfw_queue_control *
open_cfw_test_queue_generic_create(
    unsigned int length,
    unsigned int item_size,
    unsigned char queue_type
)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_GENERIC_CREATE,
        length,
        item_size
    );
    open_cfw_test_queue_control.queue_type = queue_type;
    if (open_cfw_test_queue_generic_create_success == 0U) {
        return 0;
    }
    open_cfw_test_queue_control.length = length;
    open_cfw_test_queue_control.item_size = item_size;
    open_cfw_test_queue_control.messages_waiting = 0U;
    open_cfw_test_queue_control.head =
        (signed char *)&open_cfw_test_queue_control;
    return &open_cfw_test_queue_control;
}

static void open_cfw_test_queue_initialise_mutex(
    struct open_cfw_queue_control *queue
)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_INITIALISE_MUTEX,
        queue != 0,
        0U
    );
    if (queue != 0) {
        queue->value.semaphore.mutex_holder = 0;
        queue->head = 0;
        queue->value.semaphore.recursive_call_count = 0U;
        (void)open_cfw_freertos_queue_generic_send(queue, 0, 0U, 0);
    }
}

static int open_cfw_test_queue_scheduler_state(void)
{
    return (int)open_cfw_test_queue_scheduler_state_value;
}

static void *open_cfw_test_queue_current_task(void)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_CURRENT_TASK,
        (unsigned int)open_cfw_test_queue_current_task_value,
        0U
    );
    return (void *)open_cfw_test_queue_current_task_value;
}

static void open_cfw_test_queue_enter_critical(void)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_ENTER_CRITICAL,
        0U,
        0U
    );
}

static void open_cfw_test_queue_exit_critical(void)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_EXIT_CRITICAL,
        0U,
        0U
    );
}

static int open_cfw_test_queue_copy_data(
    struct open_cfw_queue_control *queue,
    const void *item,
    int position
)
{
    unsigned int messages = queue->messages_waiting;

    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_COPY_DATA,
        (unsigned int)position,
        queue->item_size
    );
    if (queue->item_size == 0U) {
        if (queue->head == 0) {
            queue->value.semaphore.mutex_holder = 0;
        }
    } else if (position == 0) {
        memcpy(queue->write_to, item, queue->item_size);
        queue->write_to += queue->item_size;
        if (queue->write_to >= queue->value.queue.tail) {
            queue->write_to = queue->head;
        }
    } else {
        memcpy(queue->value.queue.read_from, item, queue->item_size);
        queue->value.queue.read_from -= queue->item_size;
        if (queue->value.queue.read_from < queue->head) {
            queue->value.queue.read_from =
                queue->value.queue.tail - queue->item_size;
        }
        if ((position == 2) && (messages > 0U)) {
            messages--;
        }
    }
    queue->messages_waiting = messages + 1U;
    return (int)open_cfw_test_queue_copy_yield;
}

static int open_cfw_test_queue_remove_event(
    struct open_cfw_queue_list *list
)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_REMOVE_EVENT,
        list->item_count,
        open_cfw_test_queue_remove_event_result
    );
    if (list->item_count != 0U) {
        list->item_count--;
    }
    return (int)open_cfw_test_queue_remove_event_result;
}

static void open_cfw_test_queue_yield(void)
{
    open_cfw_test_queue_log(OPEN_CFW_TEST_QUEUE_EVENT_YIELD, 0U, 0U);
}

static void open_cfw_test_queue_set_timeout(
    struct open_cfw_queue_timeout *timeout
)
{
    timeout->overflow_count = 0x12;
    timeout->time_on_entering = 0x3456789AU;
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_SET_TIMEOUT,
        0U,
        0U
    );
}

static void open_cfw_test_queue_suspend_all(void)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_SUSPEND_ALL,
        0U,
        0U
    );
}

static int open_cfw_test_queue_check_timeout(
    struct open_cfw_queue_timeout *timeout,
    unsigned int *ticks_to_wait
)
{
    unsigned int result = open_cfw_test_queue_check_timeout_result;
    unsigned int mutation = open_cfw_test_queue_check_timeout_mutation;

    (void)timeout;
    if (open_cfw_test_queue_check_timeout_calls != 0U) {
        result = open_cfw_test_queue_check_timeout_result_after_first;
        mutation =
            open_cfw_test_queue_check_timeout_mutation_after_first;
    }
    open_cfw_test_queue_check_timeout_calls++;
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_CHECK_TIMEOUT,
        *ticks_to_wait,
        result
    );
    if (mutation == 1U) {
        open_cfw_test_queue_control.messages_waiting =
            open_cfw_test_queue_control.length - 1U;
    } else if (mutation == 2U) {
        open_cfw_test_queue_control.messages_waiting = 1U;
    }
    return (int)result;
}

static int open_cfw_test_queue_is_full(
    const struct open_cfw_queue_control *queue
)
{
    return queue->messages_waiting == queue->length;
}

static void open_cfw_test_queue_place_on_event(
    struct open_cfw_queue_list *list,
    unsigned int ticks_to_wait
)
{
    list->item_count++;
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_PLACE_ON_EVENT,
        ticks_to_wait,
        list->item_count
    );
}

static void open_cfw_test_queue_unlock(
    struct open_cfw_queue_control *queue
)
{
    queue->receive_lock = (signed char)-1;
    queue->transmit_lock = (signed char)-1;
    open_cfw_test_queue_log(OPEN_CFW_TEST_QUEUE_EVENT_UNLOCK, 0U, 0U);
}

static int open_cfw_test_queue_resume_all(void)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_RESUME_ALL,
        open_cfw_test_queue_resume_all_result,
        0U
    );
    return (int)open_cfw_test_queue_resume_all_result;
}

static int open_cfw_test_queue_is_empty(
    const struct open_cfw_queue_control *queue
)
{
    return queue->messages_waiting == 0U;
}

static void *open_cfw_test_queue_increment_mutex_held(void)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_INCREMENT_MUTEX_HELD,
        0U,
        0U
    );
    return (void *)open_cfw_test_queue_mutex_holder_value;
}

static int open_cfw_test_queue_priority_inherit(void *mutex_holder)
{
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_PRIORITY_INHERIT,
        mutex_holder != 0,
        open_cfw_test_queue_priority_inherit_result
    );
    return (int)open_cfw_test_queue_priority_inherit_result;
}

static unsigned int open_cfw_test_queue_disinherit_priority(
    const struct open_cfw_queue_control *queue
)
{
    (void)queue;
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_DISINHERIT_PRIORITY,
        open_cfw_test_queue_highest_waiting_priority,
        0U
    );
    return open_cfw_test_queue_highest_waiting_priority;
}

static void open_cfw_test_queue_disinherit_after_timeout(
    void *mutex_holder,
    unsigned int highest_waiting_priority
)
{
    open_cfw_test_queue_disinherit_holder = (unsigned long)mutex_holder;
    open_cfw_test_queue_disinherit_priority_value =
        highest_waiting_priority;
    open_cfw_test_queue_log(
        OPEN_CFW_TEST_QUEUE_EVENT_DISINHERIT_AFTER_TIMEOUT,
        highest_waiting_priority,
        0U
    );
}

void open_cfw_test_queue_reset(
    unsigned int length,
    unsigned int item_size,
    unsigned int messages_waiting,
    unsigned int mutex
)
{
    unsigned int index;

    memset(&open_cfw_test_queue_control, 0, sizeof(open_cfw_test_queue_control));
    memset(open_cfw_test_queue_storage, 0, sizeof(open_cfw_test_queue_storage));
    for (index = 0U; index < OPEN_CFW_TEST_QUEUE_EVENT_CAPACITY; ++index) {
        open_cfw_test_queue_events[index] = 0U;
        open_cfw_test_queue_arguments0[index] = 0U;
        open_cfw_test_queue_arguments1[index] = 0U;
    }
    open_cfw_test_queue_event_count = 0U;
    open_cfw_test_queue_scheduler_state_value = 2U;
    open_cfw_test_queue_generic_create_success = 1U;
    open_cfw_test_queue_copy_yield = 0U;
    open_cfw_test_queue_remove_event_result = 0U;
    open_cfw_test_queue_resume_all_result = 1U;
    open_cfw_test_queue_check_timeout_result = 1U;
    open_cfw_test_queue_check_timeout_mutation = 0U;
    open_cfw_test_queue_check_timeout_result_after_first = 1U;
    open_cfw_test_queue_check_timeout_mutation_after_first = 0U;
    open_cfw_test_queue_check_timeout_calls = 0U;
    open_cfw_test_queue_priority_inherit_result = 0U;
    open_cfw_test_queue_highest_waiting_priority = 0U;
    open_cfw_test_queue_current_task_value = 0x12345678UL;
    open_cfw_test_queue_mutex_holder_value = 0x12345678UL;
    open_cfw_test_queue_disinherit_holder = 0UL;
    open_cfw_test_queue_disinherit_priority_value = 0U;
    open_cfw_test_queue_assert_count = 0U;
    open_cfw_test_queue_assert_armed = 0U;

    open_cfw_test_queue_control.head =
        mutex != 0U ? 0 : (signed char *)open_cfw_test_queue_storage;
    open_cfw_test_queue_control.write_to =
        (signed char *)open_cfw_test_queue_storage;
    open_cfw_test_queue_control.value.queue.tail =
        (signed char *)open_cfw_test_queue_storage + length * item_size;
    open_cfw_test_queue_control.value.queue.read_from =
        item_size == 0U
        ? (signed char *)open_cfw_test_queue_storage
        : (signed char *)open_cfw_test_queue_storage +
            (length - 1U) * item_size;
    open_cfw_test_queue_control.messages_waiting = messages_waiting;
    open_cfw_test_queue_control.length = length;
    open_cfw_test_queue_control.item_size = item_size;
    open_cfw_test_queue_control.receive_lock = (signed char)-1;
    open_cfw_test_queue_control.transmit_lock = (signed char)-1;
    if (mutex != 0U) {
        open_cfw_test_queue_control.value.semaphore.mutex_holder =
            (void *)0x87654321UL;
    }
}

void *open_cfw_test_queue_pointer(void)
{
    return &open_cfw_test_queue_control;
}

unsigned int open_cfw_test_queue_messages_waiting(void)
{
    return open_cfw_test_queue_control.messages_waiting;
}

unsigned int open_cfw_test_queue_send_waiters(void)
{
    return open_cfw_test_queue_control.tasks_waiting_to_send.item_count;
}

unsigned int open_cfw_test_queue_receive_waiters(void)
{
    return open_cfw_test_queue_control.tasks_waiting_to_receive.item_count;
}

void open_cfw_test_queue_set_waiters(
    unsigned int send_waiters,
    unsigned int receive_waiters
)
{
    open_cfw_test_queue_control.tasks_waiting_to_send.item_count =
        send_waiters;
    open_cfw_test_queue_control.tasks_waiting_to_receive.item_count =
        receive_waiters;
}

void open_cfw_test_queue_set_mutex_state(
    unsigned long holder,
    unsigned int recursive_count
)
{
    open_cfw_test_queue_control.value.semaphore.mutex_holder =
        (void *)holder;
    open_cfw_test_queue_control.value.semaphore.recursive_call_count =
        recursive_count;
}

unsigned long open_cfw_test_queue_mutex_holder(void)
{
    return (unsigned long)
        open_cfw_test_queue_control.value.semaphore.mutex_holder;
}

unsigned int open_cfw_test_queue_recursive_count(void)
{
    return open_cfw_test_queue_control.value.semaphore.recursive_call_count;
}

unsigned int open_cfw_test_queue_type(void)
{
    return open_cfw_test_queue_control.queue_type;
}

int open_cfw_test_queue_write_offset(void)
{
    return (int)(
        open_cfw_test_queue_control.write_to -
        (signed char *)open_cfw_test_queue_storage
    );
}

int open_cfw_test_queue_read_offset(void)
{
    return (int)(
        open_cfw_test_queue_control.value.queue.read_from -
        (signed char *)open_cfw_test_queue_storage
    );
}

unsigned char open_cfw_test_queue_storage_byte(unsigned int index)
{
    return open_cfw_test_queue_storage[index];
}

int open_cfw_test_queue_send_asserting(
    void *queue,
    const void *item,
    unsigned int ticks_to_wait,
    int copy_position
)
{
    int result;

    open_cfw_test_queue_assert_armed = 1U;
    if (setjmp(open_cfw_test_queue_assert_jump) != 0) {
        open_cfw_test_queue_assert_armed = 0U;
        return -100;
    }
    result = open_cfw_freertos_queue_generic_send(
        (struct open_cfw_queue_control *)queue,
        item,
        ticks_to_wait,
        copy_position
    );
    open_cfw_test_queue_assert_armed = 0U;
    return result;
}

int open_cfw_test_queue_take_asserting(
    void *queue,
    unsigned int ticks_to_wait
)
{
    int result;

    open_cfw_test_queue_assert_armed = 1U;
    if (setjmp(open_cfw_test_queue_assert_jump) != 0) {
        open_cfw_test_queue_assert_armed = 0U;
        return -100;
    }
    result = open_cfw_freertos_queue_semaphore_take(
        (struct open_cfw_queue_control *)queue,
        ticks_to_wait
    );
    open_cfw_test_queue_assert_armed = 0U;
    return result;
}

int open_cfw_test_queue_give_recursive_asserting(void *queue)
{
    int result;

    open_cfw_test_queue_assert_armed = 1U;
    if (setjmp(open_cfw_test_queue_assert_jump) != 0) {
        open_cfw_test_queue_assert_armed = 0U;
        return -100;
    }
    result = open_cfw_freertos_queue_give_mutex_recursive(
        (struct open_cfw_queue_control *)queue
    );
    open_cfw_test_queue_assert_armed = 0U;
    return result;
}

int open_cfw_test_queue_take_recursive_asserting(
    void *queue,
    unsigned int ticks_to_wait
)
{
    int result;

    open_cfw_test_queue_assert_armed = 1U;
    if (setjmp(open_cfw_test_queue_assert_jump) != 0) {
        open_cfw_test_queue_assert_armed = 0U;
        return -100;
    }
    result = open_cfw_freertos_queue_take_mutex_recursive(
        (struct open_cfw_queue_control *)queue,
        ticks_to_wait
    );
    open_cfw_test_queue_assert_armed = 0U;
    return result;
}
