/* SPDX-License-Identifier: MIT */

#include <stdint.h>
#include <string.h>

struct open_cfw_semaphore_take_queue;
struct open_cfw_semaphore_take_list;
struct open_cfw_semaphore_take_timeout;

static void open_cfw_take_assert(int condition);
static int open_cfw_take_scheduler_state(void);
static void open_cfw_take_enter_critical(void);
static void open_cfw_take_exit_critical(void);
static int open_cfw_take_remove_event(
    struct open_cfw_semaphore_take_list *list
);
static void open_cfw_take_yield(void);
static void open_cfw_take_set_timeout(
    struct open_cfw_semaphore_take_timeout *timeout
);
static void open_cfw_take_suspend_all(void);
static int open_cfw_take_check_timeout(
    struct open_cfw_semaphore_take_timeout *timeout,
    unsigned int *ticks
);
static int open_cfw_take_is_empty(
    const struct open_cfw_semaphore_take_queue *queue
);
static void open_cfw_take_place_on_event(
    struct open_cfw_semaphore_take_list *list,
    unsigned int ticks
);
static void open_cfw_take_unlock(
    struct open_cfw_semaphore_take_queue *queue
);
static int open_cfw_take_resume_all(void);
static void *open_cfw_take_increment_mutex_held(void);
static int open_cfw_take_priority_inherit(void *holder);
static void open_cfw_take_disinherit_after_timeout(
    void *holder,
    unsigned int priority
);

#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SKIP_ABI_ASSERTS 1
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ASSERT(condition) \
    open_cfw_take_assert((condition))
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SCHEDULER_STATE() \
    open_cfw_take_scheduler_state()
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ENTER_CRITICAL() \
    open_cfw_take_enter_critical()
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_EXIT_CRITICAL() \
    open_cfw_take_exit_critical()
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_REMOVE_EVENT(list) \
    open_cfw_take_remove_event((list))
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_YIELD() \
    open_cfw_take_yield()
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SET_TIMEOUT(timeout) \
    open_cfw_take_set_timeout((timeout))
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SUSPEND_ALL() \
    open_cfw_take_suspend_all()
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_CHECK_TIMEOUT(timeout, ticks) \
    open_cfw_take_check_timeout((timeout), (ticks))
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_IS_EMPTY(queue) \
    open_cfw_take_is_empty((queue))
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_PLACE_ON_EVENT(list, ticks) \
    open_cfw_take_place_on_event((list), (ticks))
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_UNLOCK(queue) \
    open_cfw_take_unlock((queue))
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_RESUME_ALL() \
    open_cfw_take_resume_all()
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_INCREMENT_MUTEX_HELD() \
    open_cfw_take_increment_mutex_held()
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_PRIORITY_INHERIT(holder) \
    open_cfw_take_priority_inherit((holder))
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_DISINHERIT_AFTER_TIMEOUT( \
    holder, priority \
) open_cfw_take_disinherit_after_timeout((holder), (priority))

#include "../../components/shared/freertos/runtime_freertos_queue_semaphore_take_upstream_candidate.c"

static unsigned int open_cfw_take_head_item_value;
#define OPEN_CFW_FREERTOS_DISINHERIT_LIST_LENGTH(queue) \
    (((const struct open_cfw_semaphore_take_queue *)(queue))-> \
        tasks_waiting_to_receive.item_count)
#define OPEN_CFW_FREERTOS_DISINHERIT_HEAD_ITEM_VALUE(queue) \
    (open_cfw_take_head_item_value)
#include "../../components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.c"

enum {
    OPEN_CFW_TAKE_ENTER = 1,
    OPEN_CFW_TAKE_EXIT = 2,
    OPEN_CFW_TAKE_REMOVE = 3,
    OPEN_CFW_TAKE_YIELD_EVENT = 4,
    OPEN_CFW_TAKE_SET_TIME = 5,
    OPEN_CFW_TAKE_SUSPEND = 6,
    OPEN_CFW_TAKE_CHECK = 7,
    OPEN_CFW_TAKE_PLACE = 8,
    OPEN_CFW_TAKE_UNLOCK_EVENT = 9,
    OPEN_CFW_TAKE_RESUME = 10,
    OPEN_CFW_TAKE_INCREMENT = 11,
    OPEN_CFW_TAKE_INHERIT = 12,
    OPEN_CFW_TAKE_DISINHERIT = 13,
    OPEN_CFW_TAKE_EVENT_CAPACITY = 128
};

static struct open_cfw_semaphore_take_queue open_cfw_take_queue;
static unsigned int open_cfw_take_events[OPEN_CFW_TAKE_EVENT_CAPACITY];
static unsigned int open_cfw_take_event_arguments[
    OPEN_CFW_TAKE_EVENT_CAPACITY
];
static unsigned int open_cfw_take_event_count;
static unsigned int open_cfw_take_scheduler_state_value;
static unsigned int open_cfw_take_remove_result;
static unsigned int open_cfw_take_resume_result;
static unsigned int open_cfw_take_check_first;
static unsigned int open_cfw_take_check_later;
static unsigned int open_cfw_take_mutation_first;
static unsigned int open_cfw_take_mutation_later;
static unsigned int open_cfw_take_check_calls;
static unsigned int open_cfw_take_inherit_result;
static uintptr_t open_cfw_take_increment_holder;
static uintptr_t open_cfw_take_disinherit_holder;
static unsigned int open_cfw_take_disinherit_priority;

static void open_cfw_take_log(unsigned int event, unsigned int argument)
{
    unsigned int index = open_cfw_take_event_count++;

    if (index < OPEN_CFW_TAKE_EVENT_CAPACITY) {
        open_cfw_take_events[index] = event;
        open_cfw_take_event_arguments[index] = argument;
    }
}

void open_cfw_take_reset(
    unsigned int messages,
    unsigned int mutex,
    unsigned int send_waiters,
    unsigned int receive_waiters,
    unsigned int highest_waiting_priority
)
{
    memset(&open_cfw_take_queue, 0, sizeof(open_cfw_take_queue));
    memset(open_cfw_take_events, 0, sizeof(open_cfw_take_events));
    memset(
        open_cfw_take_event_arguments,
        0,
        sizeof(open_cfw_take_event_arguments)
    );
    open_cfw_take_queue.head = mutex != 0U ? 0 : (signed char *)(uintptr_t)1U;
    open_cfw_take_queue.value.semaphore.mutex_holder =
        mutex != 0U ? (void *)(uintptr_t)0x22222222U : 0;
    open_cfw_take_queue.messages_waiting = messages;
    open_cfw_take_queue.length = 1U;
    open_cfw_take_queue.item_size = 0U;
    open_cfw_take_queue.receive_lock = -1;
    open_cfw_take_queue.transmit_lock = -1;
    open_cfw_take_queue.tasks_waiting_to_send.item_count = send_waiters;
    open_cfw_take_queue.tasks_waiting_to_receive.item_count = receive_waiters;
    open_cfw_take_head_item_value = 56U - highest_waiting_priority;
    open_cfw_take_event_count = 0U;
    open_cfw_take_scheduler_state_value = 1U;
    open_cfw_take_remove_result = 0U;
    open_cfw_take_resume_result = 1U;
    open_cfw_take_check_first = 1U;
    open_cfw_take_check_later = 1U;
    open_cfw_take_mutation_first = messages;
    open_cfw_take_mutation_later = messages;
    open_cfw_take_check_calls = 0U;
    open_cfw_take_inherit_result = 0U;
    open_cfw_take_increment_holder = (uintptr_t)0x33333333U;
    open_cfw_take_disinherit_holder = 0U;
    open_cfw_take_disinherit_priority = 0xFFFFFFFFU;
}

void open_cfw_take_configure(
    unsigned int check_first,
    unsigned int mutation_first,
    unsigned int check_later,
    unsigned int mutation_later,
    unsigned int resume_result,
    unsigned int remove_result,
    unsigned int inherit_result
)
{
    open_cfw_take_check_first = check_first;
    open_cfw_take_mutation_first = mutation_first;
    open_cfw_take_check_later = check_later;
    open_cfw_take_mutation_later = mutation_later;
    open_cfw_take_resume_result = resume_result;
    open_cfw_take_remove_result = remove_result;
    open_cfw_take_inherit_result = inherit_result;
}

int open_cfw_take_execute(unsigned int ticks)
{
    return open_cfw_freertos_queue_semaphore_take_upstream_candidate(
        &open_cfw_take_queue,
        ticks
    );
}

unsigned int open_cfw_take_get_messages(void)
{
    return open_cfw_take_queue.messages_waiting;
}

unsigned int open_cfw_take_get_send_waiters(void)
{
    return open_cfw_take_queue.tasks_waiting_to_send.item_count;
}

unsigned int open_cfw_take_get_receive_waiters(void)
{
    return open_cfw_take_queue.tasks_waiting_to_receive.item_count;
}

uintptr_t open_cfw_take_get_holder(void)
{
    return (uintptr_t)open_cfw_take_queue.value.semaphore.mutex_holder;
}

int open_cfw_take_get_receive_lock(void)
{
    return open_cfw_take_queue.receive_lock;
}

int open_cfw_take_get_transmit_lock(void)
{
    return open_cfw_take_queue.transmit_lock;
}

unsigned int open_cfw_take_get_check_calls(void)
{
    return open_cfw_take_check_calls;
}

uintptr_t open_cfw_take_get_disinherit_holder(void)
{
    return open_cfw_take_disinherit_holder;
}

unsigned int open_cfw_take_get_disinherit_priority(void)
{
    return open_cfw_take_disinherit_priority;
}

unsigned int open_cfw_take_get_event_count(void)
{
    return open_cfw_take_event_count;
}

unsigned int open_cfw_take_get_event(unsigned int index)
{
    return index < open_cfw_take_event_count ?
        open_cfw_take_events[index] : 0xFFFFFFFFU;
}

unsigned int open_cfw_take_get_event_argument(unsigned int index)
{
    return index < open_cfw_take_event_count ?
        open_cfw_take_event_arguments[index] : 0xFFFFFFFFU;
}

static void open_cfw_take_assert(int condition)
{
    if (condition == 0) {
        __builtin_trap();
    }
}

static int open_cfw_take_scheduler_state(void)
{
    return (int)open_cfw_take_scheduler_state_value;
}

static void open_cfw_take_enter_critical(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_ENTER, 0U);
}

static void open_cfw_take_exit_critical(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_EXIT, 0U);
}

static int open_cfw_take_remove_event(
    struct open_cfw_semaphore_take_list *list
)
{
    open_cfw_take_log(OPEN_CFW_TAKE_REMOVE, list->item_count);
    if (list->item_count != 0U) {
        --list->item_count;
    }
    return (int)open_cfw_take_remove_result;
}

static void open_cfw_take_yield(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_YIELD_EVENT, 0U);
}

static void open_cfw_take_set_timeout(
    struct open_cfw_semaphore_take_timeout *timeout
)
{
    timeout->overflow_count = 7;
    timeout->time_on_entering = 11U;
    open_cfw_take_log(OPEN_CFW_TAKE_SET_TIME, 0U);
}

static void open_cfw_take_suspend_all(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_SUSPEND, 0U);
}

static int open_cfw_take_check_timeout(
    struct open_cfw_semaphore_take_timeout *timeout,
    unsigned int *ticks
)
{
    unsigned int result;
    unsigned int mutation;

    (void)timeout;
    open_cfw_take_log(OPEN_CFW_TAKE_CHECK, *ticks);
    if (open_cfw_take_check_calls++ == 0U) {
        result = open_cfw_take_check_first;
        mutation = open_cfw_take_mutation_first;
    } else {
        result = open_cfw_take_check_later;
        mutation = open_cfw_take_mutation_later;
    }
    open_cfw_take_queue.messages_waiting = mutation;
    return (int)result;
}

static int open_cfw_take_is_empty(
    const struct open_cfw_semaphore_take_queue *queue
)
{
    int result;

    open_cfw_take_enter_critical();
    result = queue->messages_waiting == 0U;
    open_cfw_take_exit_critical();
    return result;
}

static void open_cfw_take_place_on_event(
    struct open_cfw_semaphore_take_list *list,
    unsigned int ticks
)
{
    ++list->item_count;
    open_cfw_take_log(OPEN_CFW_TAKE_PLACE, ticks);
}

static void open_cfw_take_unlock(
    struct open_cfw_semaphore_take_queue *queue
)
{
    open_cfw_take_enter_critical();
    queue->transmit_lock = -1;
    open_cfw_take_exit_critical();
    open_cfw_take_enter_critical();
    queue->receive_lock = -1;
    open_cfw_take_exit_critical();
}

static int open_cfw_take_resume_all(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_RESUME, 0U);
    return (int)open_cfw_take_resume_result;
}

static void *open_cfw_take_increment_mutex_held(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_INCREMENT, 0U);
    return (void *)open_cfw_take_increment_holder;
}

static int open_cfw_take_priority_inherit(void *holder)
{
    open_cfw_take_log(
        OPEN_CFW_TAKE_INHERIT,
        holder != 0 ? 1U : 0U
    );
    return (int)open_cfw_take_inherit_result;
}

static void open_cfw_take_disinherit_after_timeout(
    void *holder,
    unsigned int priority
)
{
    open_cfw_take_disinherit_holder = (uintptr_t)holder;
    open_cfw_take_disinherit_priority = priority;
    open_cfw_take_log(OPEN_CFW_TAKE_DISINHERIT, priority);
}
