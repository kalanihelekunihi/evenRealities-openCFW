/* SPDX-License-Identifier: MIT */
#include "runtime_ambiq_nema_hal_candidate.h"

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_nema_buffer) == 16U, "Nema buffer ABI changed");
_Static_assert(offsetof(struct open_cfw_nema_buffer, base_virt) == 8U, "Nema virtual address offset changed");
_Static_assert(offsetof(struct open_cfw_nema_buffer, base_phys) == 12U, "Nema physical address offset changed");
#endif

static struct open_cfw_nema_heap *select_heap(struct open_cfw_nema_hal *hal, int32_t pool)
{
    if (pool == OPEN_CFW_NEMA_POOL_ASSETS) return hal->assets_heap;
    if (pool == OPEN_CFW_NEMA_POOL_CLIPPED_PATH) return hal->cpu_heap;
    return hal->render_heap;
}

__attribute__((used, noinline))
uint32_t open_cfw_nema_reg_read_candidate(struct open_cfw_nema_hal *hal, uint32_t reg)
{
    return hal->registers[reg >> 2];
}

__attribute__((used, noinline))
void open_cfw_nema_reg_write_candidate(struct open_cfw_nema_hal *hal, uint32_t reg, uint32_t value)
{
    hal->registers[reg >> 2] = value;
}

__attribute__((used, noinline))
struct open_cfw_nema_buffer open_cfw_nema_buffer_create_pool_candidate(
    struct open_cfw_nema_hal *hal, int32_t pool, uint32_t size)
{
    struct open_cfw_nema_heap *heap = select_heap(hal, pool);
    struct open_cfw_nema_buffer buffer;
    uint32_t alignment;

    if (heap->cacheable) {
        size = (size + 31U) & ~31U;
        alignment = 32U;
    } else if (pool == OPEN_CFW_NEMA_POOL_CL ||
               pool == OPEN_CFW_NEMA_POOL_FB ||
               pool == OPEN_CFW_NEMA_POOL_ASSETS) {
        alignment = 8U;
    } else {
        alignment = 0U;
    }
    buffer.size = size;
    buffer.fd = pool;
    buffer.base_virt = hal->ports->allocate(heap->context, size, alignment);
    buffer.base_phys = (uintptr_t)buffer.base_virt;
    return buffer;
}

__attribute__((used, noinline))
void open_cfw_nema_buffer_destroy_candidate(
    struct open_cfw_nema_hal *hal, struct open_cfw_nema_buffer *buffer)
{
    struct open_cfw_nema_heap *heap = select_heap(hal, buffer->fd);
    hal->ports->release(heap->context, buffer->base_virt);
    buffer->base_virt = NULL;
    buffer->base_phys = 0U;
    buffer->size = 0U;
    buffer->fd = -1;
}

__attribute__((used, noinline))
void open_cfw_nema_buffer_flush_candidate(
    struct open_cfw_nema_hal *hal, const struct open_cfw_nema_buffer *buffer)
{
    if (select_heap(hal, buffer->fd)->cacheable)
        hal->ports->cache_clean(buffer->base_phys, buffer->size);
}

__attribute__((used, noinline))
void open_cfw_nema_buffer_invalidate_candidate(
    struct open_cfw_nema_hal *hal, const struct open_cfw_nema_buffer *buffer)
{
    if (select_heap(hal, buffer->fd)->cacheable)
        hal->ports->cache_invalidate(buffer->base_phys, buffer->size);
}

__attribute__((used, noinline))
bool open_cfw_nema_buffer_is_within_pool_candidate(
    struct open_cfw_nema_hal *hal, int32_t pool, uint32_t start, uint32_t length)
{
    struct open_cfw_nema_heap *heap = select_heap(hal, pool);
    uint32_t arena = (uint32_t)heap->arena;
    return start >= arena && start + length <= arena + heap->arena_size;
}

__attribute__((used, noinline))
void *open_cfw_nema_host_malloc_candidate(struct open_cfw_nema_hal *hal, uint32_t size)
{
    return hal->ports->allocate(hal->cpu_heap->context, size, 0U);
}

__attribute__((used, noinline))
void open_cfw_nema_host_free_candidate(struct open_cfw_nema_hal *hal, void *allocation)
{
    hal->ports->release(hal->cpu_heap->context, allocation);
}

__attribute__((used, noinline))
int32_t open_cfw_nema_wait_irq_candidate(struct open_cfw_nema_hal *hal)
{
    if (hal->ports->semaphore_acquire(hal->semaphore, 1000U) != 1) {
        hal->ports->diagnostic("GPU assert!!! nema_wait_irq timeout!!!\n");
        hal->ports->fatal();
        for (;;) { }
    }
    return 0;
}

__attribute__((used, noinline))
int32_t open_cfw_nema_wait_irq_cl_candidate(struct open_cfw_nema_hal *hal, int32_t cl_id)
{
    while (hal->last_cl_id < cl_id) (void)open_cfw_nema_wait_irq_candidate(hal);
    return 0;
}

__attribute__((used, noinline))
void open_cfw_nema_irq_candidate(struct open_cfw_nema_hal *hal)
{
    int32_t current = (int32_t)open_cfw_nema_reg_read_candidate(hal, OPEN_CFW_NEMA_CLID);
    int32_t previous;
    do {
        open_cfw_nema_reg_write_candidate(hal, OPEN_CFW_NEMA_INTERRUPT, 0U);
        hal->ports->clear_pending_irq(OPEN_CFW_NEMA_IRQ);
        previous = current;
        current = (int32_t)open_cfw_nema_reg_read_candidate(hal, OPEN_CFW_NEMA_CLID);
    } while (current != previous);
    hal->last_cl_id = current;
    if (hal->ports->semaphore_release(hal->semaphore) != 0)
        hal->ports->pend_context_switch();
    if (hal->interrupt_callback != NULL) hal->interrupt_callback(current);
}

__attribute__((used, noinline))
int32_t open_cfw_nema_sys_init_candidate(struct open_cfw_nema_hal *hal)
{
    int32_t result;
    open_cfw_nema_reg_write_candidate(hal, OPEN_CFW_NEMA_INTERRUPT, 0U);
    hal->ports->set_irq_priority(OPEN_CFW_NEMA_IRQ, 4U);
    hal->ports->enable_irq(OPEN_CFW_NEMA_IRQ);
    if (hal->semaphore == NULL)
        hal->semaphore = hal->ports->semaphore_create(1U, 0U, 3U);
    if (hal->ring.bo.base_phys == 0U)
        hal->ring.bo = open_cfw_nema_buffer_create_pool_candidate(
            hal, OPEN_CFW_NEMA_POOL_CL, 0x1300U);
    result = hal->ports->ringbuffer_init(&hal->ring, 1);
    if (result == 0) hal->last_cl_id = -1;
    return result;
}

__attribute__((used, noinline))
void open_cfw_nema_reset_last_cl_id_candidate(struct open_cfw_nema_hal *hal)
{
    hal->last_cl_id = -1;
}

__attribute__((used, noinline))
int32_t open_cfw_nema_get_last_cl_id_candidate(const struct open_cfw_nema_hal *hal)
{
    return hal->last_cl_id;
}

__attribute__((used, noinline))
int32_t open_cfw_nema_get_last_submission_id_candidate(const struct open_cfw_nema_hal *hal)
{
    return hal->ring.last_submission_id;
}
