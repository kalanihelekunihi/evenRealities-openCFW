#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static uint32_t test_irq;
static int test_malloc_fail_call;
static int test_semaphore_fail;
static size_t test_malloc_calls;
static size_t test_free_calls;
static size_t test_sem_calls;
static size_t test_first_size;
static size_t test_second_size;
static uintptr_t test_freed;
static uintptr_t test_sem_buffer;
static uint32_t test_sem_maximum;
static uint32_t test_sem_initial;

uint32_t open_cfw_cmsis_irq_context(void) { return test_irq; }
void *open_cfw_freertos_heap4_malloc(uint32_t size)
{
    size_t allocation = size;
    test_malloc_calls++;
    if (test_malloc_calls == 1U) test_first_size = size;
    if (test_malloc_calls == 2U) test_second_size = size;
    if ((int)test_malloc_calls == test_malloc_fail_call) return NULL;
    if (allocation < 256U) allocation = 256U;
    return calloc(1U, allocation);
}
void open_cfw_freertos_heap4_free(void *memory)
{
    test_free_calls++;
    test_freed = (uintptr_t)memory;
    free(memory);
}
void *open_cfw_freertos_queue_create_counting_semaphore_static(
    uint32_t maximum_count,
    uint32_t initial_count,
    void *static_queue
)
{
    test_sem_calls++;
    test_sem_maximum = maximum_count;
    test_sem_initial = initial_count;
    test_sem_buffer = (uintptr_t)static_queue;
    return test_semaphore_fail ? NULL : (void *)(uintptr_t)0x5150U;
}

#include "../../components/apollo_main/core_overlay/runtime_cmsis_memory_pool_new.c"

static open_cfw_cmsis_mpool_control test_static_control;
static unsigned char test_static_array[512];
static open_cfw_cmsis_mpool_control *test_last_pool;

void open_cfw_test_mpool_reset(
    uint32_t irq,
    int malloc_fail_call,
    int semaphore_fail,
    uintptr_t stale_array
)
{
    test_irq = irq;
    test_malloc_fail_call = malloc_fail_call;
    test_semaphore_fail = semaphore_fail;
    test_malloc_calls = 0U;
    test_free_calls = 0U;
    test_sem_calls = 0U;
    test_first_size = 0U;
    test_second_size = 0U;
    test_freed = 0U;
    test_sem_buffer = 0U;
    test_sem_maximum = 0U;
    test_sem_initial = 0U;
    memset(&test_static_control, 0, sizeof(test_static_control));
    memset(test_static_array, 0, sizeof(test_static_array));
    test_static_control.mem_arr = (unsigned char *)stale_array;
    test_last_pool = NULL;
}

void *open_cfw_test_mpool_call(
    uint32_t count,
    uint32_t size,
    uint32_t use_attr,
    uintptr_t cb_memory,
    uint32_t cb_size,
    uintptr_t array_memory,
    uint32_t array_size,
    uintptr_t name
)
{
    open_cfw_cmsis_mpool_attr attr;
    if (cb_memory == 1U) cb_memory = (uintptr_t)&test_static_control;
    if (array_memory == 1U) array_memory = (uintptr_t)test_static_array;
    attr.name = (const char *)name;
    attr.attr_bits = 0U;
    attr.cb_mem = (void *)cb_memory;
    attr.cb_size = cb_size;
    attr.mp_mem = (void *)array_memory;
    attr.mp_size = array_size;
    test_last_pool = (open_cfw_cmsis_mpool_control *)
        open_cfw_cmsis_memory_pool_new(count, size, use_attr ? &attr : NULL);
    return test_last_pool;
}

#define GETTER(name, expression) \
    uintptr_t open_cfw_test_mpool_##name(void) { return (uintptr_t)(expression); }
GETTER(malloc_calls, test_malloc_calls)
GETTER(free_calls, test_free_calls)
GETTER(sem_calls, test_sem_calls)
GETTER(first_size, test_first_size)
GETTER(second_size, test_second_size)
GETTER(freed, test_freed)
GETTER(sem_buffer, test_sem_buffer)
GETTER(sem_maximum, test_sem_maximum)
GETTER(sem_initial, test_sem_initial)
GETTER(static_control, &test_static_control)
GETTER(static_array, test_static_array)
GETTER(head, test_last_pool ? test_last_pool->head : NULL)
GETTER(sem, test_last_pool ? test_last_pool->sem : NULL)
GETTER(mem_arr, test_last_pool ? test_last_pool->mem_arr : NULL)
GETTER(mem_sz, test_last_pool ? test_last_pool->mem_sz : 0U)
GETTER(name, test_last_pool ? test_last_pool->name : NULL)
GETTER(block_size, test_last_pool ? test_last_pool->bl_sz : 0U)
GETTER(block_count, test_last_pool ? test_last_pool->bl_cnt : 0U)
GETTER(index, test_last_pool ? test_last_pool->n : 0U)
GETTER(status, test_last_pool ? test_last_pool->status : 0U)
