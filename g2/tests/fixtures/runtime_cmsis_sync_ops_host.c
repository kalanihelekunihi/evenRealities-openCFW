#include <stdint.h>

static uint32_t open_cfw_test_irq;
static int32_t open_cfw_test_take_recursive_result;
static int32_t open_cfw_test_take_result;
static int32_t open_cfw_test_give_recursive_result;
static int32_t open_cfw_test_send_result;
static int32_t open_cfw_test_give_isr_result;
static int32_t open_cfw_test_give_isr_yield;
static uint32_t open_cfw_test_take_recursive_calls;
static uint32_t open_cfw_test_take_calls;
static uint32_t open_cfw_test_give_recursive_calls;
static uint32_t open_cfw_test_send_calls;
static uint32_t open_cfw_test_give_isr_calls;
static uint32_t open_cfw_test_pendsv_calls;
static void *open_cfw_test_handle;
static uint32_t open_cfw_test_timeout;

uint32_t open_cfw_cmsis_irq_context(void) { return open_cfw_test_irq; }

int32_t open_cfw_freertos_queue_take_mutex_recursive(
    void *mutex,
    uint32_t timeout
)
{
    open_cfw_test_take_recursive_calls += 1U;
    open_cfw_test_handle = mutex;
    open_cfw_test_timeout = timeout;
    return open_cfw_test_take_recursive_result;
}

int32_t open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    void *mutex,
    uint32_t timeout
)
{
    open_cfw_test_take_calls += 1U;
    open_cfw_test_handle = mutex;
    open_cfw_test_timeout = timeout;
    return open_cfw_test_take_result;
}

int32_t open_cfw_freertos_queue_give_mutex_recursive(void *mutex)
{
    open_cfw_test_give_recursive_calls += 1U;
    open_cfw_test_handle = mutex;
    return open_cfw_test_give_recursive_result;
}

int32_t open_cfw_freertos_queue_generic_send(
    void *queue,
    const void *item,
    uint32_t timeout,
    int32_t copy_position
)
{
    (void)item;
    (void)copy_position;
    open_cfw_test_send_calls += 1U;
    open_cfw_test_handle = queue;
    open_cfw_test_timeout = timeout;
    return open_cfw_test_send_result;
}

int32_t open_cfw_freertos_queue_give_from_isr(
    void *queue,
    int32_t *higher_priority_task_woken
)
{
    open_cfw_test_give_isr_calls += 1U;
    open_cfw_test_handle = queue;
    *higher_priority_task_woken = open_cfw_test_give_isr_yield;
    return open_cfw_test_give_isr_result;
}

#define OPEN_CFW_CMSIS_SYNC_PENDSV_SET() \
    do { open_cfw_test_pendsv_calls += 1U; } while (0)

#include "../../components/apollo_main/core_overlay/runtime_cmsis_sync_ops.c"

void open_cfw_test_sync_reset(
    uint32_t irq,
    int32_t take_recursive_result,
    int32_t take_result,
    int32_t give_recursive_result,
    int32_t send_result,
    int32_t give_isr_result,
    int32_t give_isr_yield
)
{
    open_cfw_test_irq = irq;
    open_cfw_test_take_recursive_result = take_recursive_result;
    open_cfw_test_take_result = take_result;
    open_cfw_test_give_recursive_result = give_recursive_result;
    open_cfw_test_send_result = send_result;
    open_cfw_test_give_isr_result = give_isr_result;
    open_cfw_test_give_isr_yield = give_isr_yield;
    open_cfw_test_take_recursive_calls = 0U;
    open_cfw_test_take_calls = 0U;
    open_cfw_test_give_recursive_calls = 0U;
    open_cfw_test_send_calls = 0U;
    open_cfw_test_give_isr_calls = 0U;
    open_cfw_test_pendsv_calls = 0U;
    open_cfw_test_handle = (void *)0;
    open_cfw_test_timeout = 0U;
}

uint32_t open_cfw_test_sync_take_recursive_calls(void)
{ return open_cfw_test_take_recursive_calls; }
uint32_t open_cfw_test_sync_take_calls(void)
{ return open_cfw_test_take_calls; }
uint32_t open_cfw_test_sync_give_recursive_calls(void)
{ return open_cfw_test_give_recursive_calls; }
uint32_t open_cfw_test_sync_send_calls(void)
{ return open_cfw_test_send_calls; }
uint32_t open_cfw_test_sync_give_isr_calls(void)
{ return open_cfw_test_give_isr_calls; }
uint32_t open_cfw_test_sync_pendsv_calls(void)
{ return open_cfw_test_pendsv_calls; }
uintptr_t open_cfw_test_sync_handle(void)
{ return (uintptr_t)open_cfw_test_handle; }
uint32_t open_cfw_test_sync_timeout(void)
{ return open_cfw_test_timeout; }
