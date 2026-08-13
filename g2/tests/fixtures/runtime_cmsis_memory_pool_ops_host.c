#include <stdint.h>
#include <string.h>

static uint32_t open_cfw_test_pool_ops_irq;
static int32_t open_cfw_test_pool_ops_take_result;
static uint32_t open_cfw_test_pool_ops_count;
static int32_t open_cfw_test_pool_ops_give_result;
static int32_t open_cfw_test_pool_ops_yield;
static uint32_t open_cfw_test_pool_ops_invalidate_after_take;
static uint32_t open_cfw_test_pool_ops_take_calls;
static uint32_t open_cfw_test_pool_ops_isr_take_calls;
static uint32_t open_cfw_test_pool_ops_count_calls;
static uint32_t open_cfw_test_pool_ops_isr_count_calls;
static uint32_t open_cfw_test_pool_ops_give_calls;
static uint32_t open_cfw_test_pool_ops_isr_give_calls;
static uint32_t open_cfw_test_pool_ops_enter_calls;
static uint32_t open_cfw_test_pool_ops_exit_calls;
static uint32_t open_cfw_test_pool_ops_set_mask_calls;
static uint32_t open_cfw_test_pool_ops_clear_mask_calls;
static uint32_t open_cfw_test_pool_ops_pendsv;

uint32_t open_cfw_cmsis_irq_context(void);
int32_t open_cfw_freertos_queue_receive_from_isr(void *, void *, int32_t *);
int32_t open_cfw_freertos_queue_semaphore_take_upstream_candidate(void *, uint32_t);
void open_cfw_freertos_port_enter_critical(void);
void open_cfw_freertos_port_exit_critical(void);
uint32_t ulSetInterruptMask(void);
void vClearInterruptMask(uint32_t);
uint32_t open_cfw_freertos_queue_messages_waiting(void *);
uint32_t open_cfw_freertos_queue_messages_waiting_from_isr(void *);
int32_t open_cfw_freertos_queue_give_from_isr(void *, int32_t *);
int32_t open_cfw_freertos_queue_generic_send(void *, const void *, uint32_t, int32_t);

#define OPEN_CFW_CMSIS_POOL_OPS_PENDSV_SET() (++open_cfw_test_pool_ops_pendsv)
#include "../../components/apollo_main/core_overlay/runtime_cmsis_memory_pool_ops.c"

static open_cfw_cmsis_pool_ops_control open_cfw_test_pool_ops_pool;
static uint8_t open_cfw_test_pool_ops_array[64];

uint32_t open_cfw_cmsis_irq_context(void)
{
    return open_cfw_test_pool_ops_irq;
}

static void open_cfw_test_pool_ops_maybe_invalidate(void)
{
    if (open_cfw_test_pool_ops_invalidate_after_take != 0U) {
        open_cfw_test_pool_ops_pool.status = 0U;
    }
}

int32_t open_cfw_freertos_queue_receive_from_isr(
    void *queue,
    void *buffer,
    int32_t *higher_priority_task_woken
)
{
    (void)queue;
    (void)buffer;
    (void)higher_priority_task_woken;
    ++open_cfw_test_pool_ops_isr_take_calls;
    open_cfw_test_pool_ops_maybe_invalidate();
    return open_cfw_test_pool_ops_take_result;
}

int32_t open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    void *queue,
    uint32_t timeout
)
{
    (void)queue;
    (void)timeout;
    ++open_cfw_test_pool_ops_take_calls;
    open_cfw_test_pool_ops_maybe_invalidate();
    return open_cfw_test_pool_ops_take_result;
}

void open_cfw_freertos_port_enter_critical(void)
{
    ++open_cfw_test_pool_ops_enter_calls;
}

void open_cfw_freertos_port_exit_critical(void)
{
    ++open_cfw_test_pool_ops_exit_calls;
}

uint32_t ulSetInterruptMask(void)
{
    ++open_cfw_test_pool_ops_set_mask_calls;
    return 0x5AU;
}

void vClearInterruptMask(uint32_t mask)
{
    if (mask == 0x5AU) {
        ++open_cfw_test_pool_ops_clear_mask_calls;
    }
}

uint32_t open_cfw_freertos_queue_messages_waiting(void *queue)
{
    (void)queue;
    ++open_cfw_test_pool_ops_count_calls;
    return open_cfw_test_pool_ops_count;
}

uint32_t open_cfw_freertos_queue_messages_waiting_from_isr(void *queue)
{
    (void)queue;
    ++open_cfw_test_pool_ops_isr_count_calls;
    return open_cfw_test_pool_ops_count;
}

int32_t open_cfw_freertos_queue_give_from_isr(
    void *queue,
    int32_t *higher_priority_task_woken
)
{
    (void)queue;
    ++open_cfw_test_pool_ops_isr_give_calls;
    *higher_priority_task_woken = open_cfw_test_pool_ops_yield;
    return open_cfw_test_pool_ops_give_result;
}

int32_t open_cfw_freertos_queue_generic_send(
    void *queue,
    const void *item,
    uint32_t timeout,
    int32_t copy_position
)
{
    (void)queue;
    (void)item;
    (void)timeout;
    (void)copy_position;
    ++open_cfw_test_pool_ops_give_calls;
    return open_cfw_test_pool_ops_give_result;
}

void open_cfw_test_pool_ops_reset(
    uint32_t irq,
    int32_t take_result,
    uint32_t count,
    int32_t give_result,
    int32_t yield,
    uint32_t invalidate_after_take
)
{
    memset(&open_cfw_test_pool_ops_pool, 0,
           sizeof(open_cfw_test_pool_ops_pool));
    memset(open_cfw_test_pool_ops_array, 0,
           sizeof(open_cfw_test_pool_ops_array));
    open_cfw_test_pool_ops_pool.sem = (void *)(uintptr_t)0x5150U;
    open_cfw_test_pool_ops_pool.mem_arr = open_cfw_test_pool_ops_array;
    open_cfw_test_pool_ops_pool.mem_sz = sizeof(open_cfw_test_pool_ops_array);
    open_cfw_test_pool_ops_pool.bl_sz = 4U;
    open_cfw_test_pool_ops_pool.bl_cnt = 4U;
    open_cfw_test_pool_ops_pool.status = OPEN_CFW_CMSIS_POOL_OPS_STATUS;
    open_cfw_test_pool_ops_irq = irq;
    open_cfw_test_pool_ops_take_result = take_result;
    open_cfw_test_pool_ops_count = count;
    open_cfw_test_pool_ops_give_result = give_result;
    open_cfw_test_pool_ops_yield = yield;
    open_cfw_test_pool_ops_invalidate_after_take = invalidate_after_take;
    open_cfw_test_pool_ops_take_calls = 0U;
    open_cfw_test_pool_ops_isr_take_calls = 0U;
    open_cfw_test_pool_ops_count_calls = 0U;
    open_cfw_test_pool_ops_isr_count_calls = 0U;
    open_cfw_test_pool_ops_give_calls = 0U;
    open_cfw_test_pool_ops_isr_give_calls = 0U;
    open_cfw_test_pool_ops_enter_calls = 0U;
    open_cfw_test_pool_ops_exit_calls = 0U;
    open_cfw_test_pool_ops_set_mask_calls = 0U;
    open_cfw_test_pool_ops_clear_mask_calls = 0U;
    open_cfw_test_pool_ops_pendsv = 0U;
}

void open_cfw_test_pool_ops_set_status(uint32_t status)
{
    open_cfw_test_pool_ops_pool.status = status;
}

void open_cfw_test_pool_ops_set_head(uint32_t first, uint32_t second)
{
    open_cfw_cmsis_pool_ops_block *first_block =
        (open_cfw_cmsis_pool_ops_block *)&open_cfw_test_pool_ops_array[first];
    open_cfw_cmsis_pool_ops_block *second_block =
        (open_cfw_cmsis_pool_ops_block *)&open_cfw_test_pool_ops_array[second];
    first_block->next = second_block;
    second_block->next = (open_cfw_cmsis_pool_ops_block *)0;
    open_cfw_test_pool_ops_pool.head = first_block;
}

uintptr_t open_cfw_test_pool_ops_alloc(uint32_t timeout)
{
    void *block = open_cfw_cmsis_memory_pool_alloc(
        &open_cfw_test_pool_ops_pool,
        timeout
    );
    if (block == (void *)0) {
        return (uintptr_t)-1;
    }
    return (uintptr_t)((uint8_t *)block - open_cfw_test_pool_ops_array);
}

uintptr_t open_cfw_test_pool_ops_alloc_null(uint32_t timeout)
{
    return (uintptr_t)open_cfw_cmsis_memory_pool_alloc((void *)0, timeout);
}

int32_t open_cfw_test_pool_ops_free(int32_t offset)
{
    void *block = offset == -1 ? (void *)0 :
        (void *)(open_cfw_test_pool_ops_array + offset);
    return open_cfw_cmsis_memory_pool_free(
        &open_cfw_test_pool_ops_pool,
        block
    );
}

int32_t open_cfw_test_pool_ops_free_null_pool(void)
{
    return open_cfw_cmsis_memory_pool_free(
        (void *)0,
        open_cfw_test_pool_ops_array
    );
}

int32_t open_cfw_test_pool_ops_head_offset(void)
{
    if (open_cfw_test_pool_ops_pool.head == 0) {
        return -1;
    }
    return (int32_t)((uint8_t *)open_cfw_test_pool_ops_pool.head -
                     open_cfw_test_pool_ops_array);
}

uint32_t open_cfw_test_pool_ops_index(void)
{
    return open_cfw_test_pool_ops_pool.n;
}

#define OPEN_CFW_TEST_POOL_OPS_GETTER(name) \
    uint32_t open_cfw_test_pool_ops_get_##name(void) \
    { \
        return open_cfw_test_pool_ops_##name; \
    }

OPEN_CFW_TEST_POOL_OPS_GETTER(take_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(isr_take_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(count_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(isr_count_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(give_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(isr_give_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(enter_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(exit_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(set_mask_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(clear_mask_calls)
OPEN_CFW_TEST_POOL_OPS_GETTER(pendsv)
