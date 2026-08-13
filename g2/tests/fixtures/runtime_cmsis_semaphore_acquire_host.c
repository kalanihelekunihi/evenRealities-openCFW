#include <stdint.h>

static uint32_t open_cfw_test_sem_irq;
static int32_t open_cfw_test_sem_isr_result;
static int32_t open_cfw_test_sem_task_result;
static int32_t open_cfw_test_sem_yield;
static uint32_t open_cfw_test_sem_isr_calls;
static uint32_t open_cfw_test_sem_task_calls;
static uint32_t open_cfw_test_sem_pendsv;
static uintptr_t open_cfw_test_sem_queue;
static uint32_t open_cfw_test_sem_timeout;
static uintptr_t open_cfw_test_sem_buffer;

uint32_t open_cfw_cmsis_irq_context(void)
{
    return open_cfw_test_sem_irq;
}

int32_t open_cfw_freertos_queue_receive_from_isr(
    void *queue,
    void *buffer,
    int32_t *higher_priority_task_woken
)
{
    ++open_cfw_test_sem_isr_calls;
    open_cfw_test_sem_queue = (uintptr_t)queue;
    open_cfw_test_sem_buffer = (uintptr_t)buffer;
    *higher_priority_task_woken = open_cfw_test_sem_yield;
    return open_cfw_test_sem_isr_result;
}

int32_t open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    void *queue,
    uint32_t timeout
)
{
    ++open_cfw_test_sem_task_calls;
    open_cfw_test_sem_queue = (uintptr_t)queue;
    open_cfw_test_sem_timeout = timeout;
    return open_cfw_test_sem_task_result;
}

#define OPEN_CFW_CMSIS_SEM_ACQUIRE_PENDSV_SET() \
    (++open_cfw_test_sem_pendsv)

#include "../../components/apollo_main/core_overlay/runtime_cmsis_semaphore_acquire.c"

void open_cfw_test_sem_reset(
    uint32_t irq,
    int32_t isr_result,
    int32_t task_result,
    int32_t yield
)
{
    open_cfw_test_sem_irq = irq;
    open_cfw_test_sem_isr_result = isr_result;
    open_cfw_test_sem_task_result = task_result;
    open_cfw_test_sem_yield = yield;
    open_cfw_test_sem_isr_calls = 0U;
    open_cfw_test_sem_task_calls = 0U;
    open_cfw_test_sem_pendsv = 0U;
    open_cfw_test_sem_queue = 0U;
    open_cfw_test_sem_timeout = 0U;
    open_cfw_test_sem_buffer = 1U;
}

int32_t open_cfw_test_sem_call(uintptr_t semaphore, uint32_t timeout)
{
    return open_cfw_cmsis_semaphore_acquire((void *)semaphore, timeout);
}

#define OPEN_CFW_TEST_SEM_GETTER(name, type) \
    type open_cfw_test_sem_get_##name(void) \
    { \
        return open_cfw_test_sem_##name; \
    }

OPEN_CFW_TEST_SEM_GETTER(isr_calls, uint32_t)
OPEN_CFW_TEST_SEM_GETTER(task_calls, uint32_t)
OPEN_CFW_TEST_SEM_GETTER(pendsv, uint32_t)
OPEN_CFW_TEST_SEM_GETTER(queue, uintptr_t)
OPEN_CFW_TEST_SEM_GETTER(timeout, uint32_t)
OPEN_CFW_TEST_SEM_GETTER(buffer, uintptr_t)
