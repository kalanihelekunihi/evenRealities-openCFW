#include <stdarg.h>

void *open_cfw_test_lv_display_lock_mutex;
int open_cfw_test_lv_display_lock_take_result;
int open_cfw_test_lv_display_lock_context_result;
void *open_cfw_test_lv_display_lock_create_result;
unsigned int open_cfw_test_lv_display_lock_trace_count;
unsigned int open_cfw_test_lv_display_lock_trace[4];
unsigned int open_cfw_test_lv_display_lock_take_calls;
void *open_cfw_test_lv_display_lock_take_mutex;
unsigned int open_cfw_test_lv_display_lock_take_timeout;
unsigned int open_cfw_test_lv_display_lock_context_calls;
unsigned int open_cfw_test_lv_display_lock_give_task_calls;
void *open_cfw_test_lv_display_lock_give_task_mutex;
unsigned int open_cfw_test_lv_display_lock_give_task_arguments[3];
unsigned int open_cfw_test_lv_display_lock_give_irq_calls;
void *open_cfw_test_lv_display_lock_give_irq_mutex;
unsigned int open_cfw_test_lv_display_lock_give_irq_value;
unsigned int open_cfw_test_lv_display_lock_create_calls;
unsigned int open_cfw_test_lv_display_lock_create_arguments[3];
unsigned int open_cfw_test_lv_display_lock_log_calls;
unsigned int open_cfw_test_lv_display_lock_log_level;
const void *open_cfw_test_lv_display_lock_log_file;
unsigned int open_cfw_test_lv_display_lock_log_line;
const void *open_cfw_test_lv_display_lock_log_function;
const void *open_cfw_test_lv_display_lock_log_argument;
unsigned int open_cfw_test_lv_display_lock_setup_calls;

static void open_cfw_test_lv_display_lock_record(unsigned int value)
{
    unsigned int index = open_cfw_test_lv_display_lock_trace_count++;

    if (index < 4U) {
        open_cfw_test_lv_display_lock_trace[index] = value;
    }
}

int open_cfw_test_lv_display_lock_take(void *mutex, unsigned int timeout)
{
    open_cfw_test_lv_display_lock_record(1U);
    open_cfw_test_lv_display_lock_take_calls += 1U;
    open_cfw_test_lv_display_lock_take_mutex = mutex;
    open_cfw_test_lv_display_lock_take_timeout = timeout;
    return open_cfw_test_lv_display_lock_take_result;
}

int open_cfw_test_lv_display_lock_context(void)
{
    open_cfw_test_lv_display_lock_record(1U);
    open_cfw_test_lv_display_lock_context_calls += 1U;
    return open_cfw_test_lv_display_lock_context_result;
}

void open_cfw_test_lv_display_lock_give_task(
    void *mutex,
    unsigned int first,
    unsigned int second,
    unsigned int third
)
{
    open_cfw_test_lv_display_lock_record(2U);
    open_cfw_test_lv_display_lock_give_task_calls += 1U;
    open_cfw_test_lv_display_lock_give_task_mutex = mutex;
    open_cfw_test_lv_display_lock_give_task_arguments[0] = first;
    open_cfw_test_lv_display_lock_give_task_arguments[1] = second;
    open_cfw_test_lv_display_lock_give_task_arguments[2] = third;
}

void open_cfw_test_lv_display_lock_give_irq(
    void *mutex,
    unsigned int value
)
{
    open_cfw_test_lv_display_lock_record(2U);
    open_cfw_test_lv_display_lock_give_irq_calls += 1U;
    open_cfw_test_lv_display_lock_give_irq_mutex = mutex;
    open_cfw_test_lv_display_lock_give_irq_value = value;
}

void *open_cfw_test_lv_display_lock_create(
    unsigned int count,
    unsigned int flags,
    unsigned int kind
)
{
    open_cfw_test_lv_display_lock_record(1U);
    open_cfw_test_lv_display_lock_create_calls += 1U;
    open_cfw_test_lv_display_lock_create_arguments[0] = count;
    open_cfw_test_lv_display_lock_create_arguments[1] = flags;
    open_cfw_test_lv_display_lock_create_arguments[2] = kind;
    return open_cfw_test_lv_display_lock_create_result;
}

void open_cfw_test_lv_display_lock_log(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
)
{
    va_list arguments;

    open_cfw_test_lv_display_lock_record(3U);
    open_cfw_test_lv_display_lock_log_calls += 1U;
    open_cfw_test_lv_display_lock_log_level = level;
    open_cfw_test_lv_display_lock_log_file = file;
    open_cfw_test_lv_display_lock_log_line = line;
    open_cfw_test_lv_display_lock_log_function = function;
    va_start(arguments, function);
    open_cfw_test_lv_display_lock_log_argument =
        va_arg(arguments, const void *);
    va_end(arguments);
}

void open_cfw_test_lv_display_lock_setup(void)
{
    open_cfw_test_lv_display_lock_record(4U);
    open_cfw_test_lv_display_lock_setup_calls += 1U;
}

#define OPEN_CFW_LV_DISPLAY_LOCK_MUTEX \
    open_cfw_test_lv_display_lock_mutex
#define OPEN_CFW_LV_DISPLAY_LOCK_TAKE(mutex, timeout) \
    open_cfw_test_lv_display_lock_take((mutex), (timeout))
#define OPEN_CFW_LV_DISPLAY_LOCK_CONTEXT() \
    open_cfw_test_lv_display_lock_context()
#define OPEN_CFW_LV_DISPLAY_LOCK_GIVE_TASK(mutex, first, second, third) \
    open_cfw_test_lv_display_lock_give_task( \
        (mutex), \
        (first), \
        (second), \
        (third) \
    )
#define OPEN_CFW_LV_DISPLAY_LOCK_GIVE_IRQ(mutex, value) \
    open_cfw_test_lv_display_lock_give_irq((mutex), (value))
#define OPEN_CFW_LV_DISPLAY_LOCK_CREATE(count, flags, kind) \
    open_cfw_test_lv_display_lock_create((count), (flags), (kind))
#define OPEN_CFW_LV_DISPLAY_LOCK_LOG open_cfw_test_lv_display_lock_log
#define OPEN_CFW_LV_DISPLAY_LOCK_SETUP() \
    open_cfw_test_lv_display_lock_setup()

#include "../../components/apollo_main/core_overlay/lv_display_lock.c"
