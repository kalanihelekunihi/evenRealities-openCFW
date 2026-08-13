/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded, freestanding adapters for CMSIS-FreeRTOS v10.5.1
 * osMemoryPoolAlloc(), osMemoryPoolFree(), CreateBlock(), AllocBlock(), and
 * FreeBlock() at commit d213f261b5be6bb29a7cce8b84071706b72f4d53.
 */

typedef __UINT8_TYPE__ open_cfw_cmsis_pool_ops_uint8;
typedef __UINT32_TYPE__ open_cfw_cmsis_pool_ops_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_pool_ops_int32;
typedef __UINTPTR_TYPE__ open_cfw_cmsis_pool_ops_uintptr;

typedef struct open_cfw_cmsis_pool_ops_block {
    struct open_cfw_cmsis_pool_ops_block *next;
} open_cfw_cmsis_pool_ops_block;

typedef struct {
    open_cfw_cmsis_pool_ops_block *head;
    void *sem;
    open_cfw_cmsis_pool_ops_uint8 *mem_arr;
    open_cfw_cmsis_pool_ops_uint32 mem_sz;
    const char *name;
    open_cfw_cmsis_pool_ops_uint32 bl_sz;
    open_cfw_cmsis_pool_ops_uint32 bl_cnt;
    open_cfw_cmsis_pool_ops_uint32 n;
    volatile open_cfw_cmsis_pool_ops_uint32 status;
    open_cfw_cmsis_pool_ops_uint32 static_semaphore_words[20];
} open_cfw_cmsis_pool_ops_control;

enum {
    OPEN_CFW_CMSIS_POOL_OPS_STATUS = 0x5EED0000U,
    OPEN_CFW_CMSIS_POOL_OPS_OK = 0,
    OPEN_CFW_CMSIS_POOL_OPS_ERROR_RESOURCE = -3,
    OPEN_CFW_CMSIS_POOL_OPS_ERROR_PARAMETER = -4
};

#if __SIZEOF_POINTER__ == 4
_Static_assert(sizeof(open_cfw_cmsis_pool_ops_control) == 0x74U,
               "G2 MemPool_t ABI must remain 116 bytes");
#endif

extern open_cfw_cmsis_pool_ops_uint32 open_cfw_cmsis_irq_context(void);
extern open_cfw_cmsis_pool_ops_int32
open_cfw_freertos_queue_receive_from_isr(
    void *queue,
    void *buffer,
    open_cfw_cmsis_pool_ops_int32 *higher_priority_task_woken
);
extern open_cfw_cmsis_pool_ops_int32
open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    void *queue,
    open_cfw_cmsis_pool_ops_uint32 timeout
);
extern void open_cfw_freertos_port_enter_critical(void);
extern void open_cfw_freertos_port_exit_critical(void);
extern open_cfw_cmsis_pool_ops_uint32 ulSetInterruptMask(void);
extern void vClearInterruptMask(open_cfw_cmsis_pool_ops_uint32 mask);
extern open_cfw_cmsis_pool_ops_uint32
open_cfw_freertos_queue_messages_waiting(void *queue);
extern open_cfw_cmsis_pool_ops_uint32
open_cfw_freertos_queue_messages_waiting_from_isr(void *queue);
extern open_cfw_cmsis_pool_ops_int32 open_cfw_freertos_queue_give_from_isr(
    void *queue,
    open_cfw_cmsis_pool_ops_int32 *higher_priority_task_woken
);
extern open_cfw_cmsis_pool_ops_int32 open_cfw_freertos_queue_generic_send(
    void *queue,
    const void *item,
    open_cfw_cmsis_pool_ops_uint32 timeout,
    open_cfw_cmsis_pool_ops_int32 copy_position
);

#ifndef OPEN_CFW_CMSIS_POOL_OPS_PENDSV_SET
#define OPEN_CFW_CMSIS_POOL_OPS_PENDSV_SET() \
    (*(volatile open_cfw_cmsis_pool_ops_uint32 *) \
        (open_cfw_cmsis_pool_ops_uintptr)0xE000ED04U = 0x10000000U)
#endif

__attribute__((used, noinline))
void *open_cfw_cmsis_memory_pool_create_block(
    open_cfw_cmsis_pool_ops_control *pool
)
{
    void *block = (void *)0;

    if (pool->n < pool->bl_cnt) {
        block = pool->mem_arr + (pool->bl_sz * pool->n);
        pool->n += 1U;
    }
    return block;
}

__attribute__((used, noinline))
void *open_cfw_cmsis_memory_pool_alloc_block(
    open_cfw_cmsis_pool_ops_control *pool
)
{
    open_cfw_cmsis_pool_ops_block *block = pool->head;

    if (block != (open_cfw_cmsis_pool_ops_block *)0) {
        pool->head = block->next;
    }
    return block;
}

__attribute__((used, noinline))
void open_cfw_cmsis_memory_pool_free_block(
    open_cfw_cmsis_pool_ops_control *pool,
    void *block
)
{
    open_cfw_cmsis_pool_ops_block *entry =
        (open_cfw_cmsis_pool_ops_block *)block;

    entry->next = pool->head;
    pool->head = entry;
}

__attribute__((used, noinline))
void *open_cfw_cmsis_memory_pool_alloc(
    void *pool_id,
    open_cfw_cmsis_pool_ops_uint32 timeout
)
{
    open_cfw_cmsis_pool_ops_control *pool =
        (open_cfw_cmsis_pool_ops_control *)pool_id;
    void *block = (void *)0;
    open_cfw_cmsis_pool_ops_uint32 mask;

    if (pool == (open_cfw_cmsis_pool_ops_control *)0) {
        return (void *)0;
    }
    if ((pool->status & OPEN_CFW_CMSIS_POOL_OPS_STATUS) !=
        OPEN_CFW_CMSIS_POOL_OPS_STATUS) {
        return (void *)0;
    }

    if (open_cfw_cmsis_irq_context() != 0U) {
        if (
            (timeout == 0U) &&
            (open_cfw_freertos_queue_receive_from_isr(
                pool->sem,
                (void *)0,
                (open_cfw_cmsis_pool_ops_int32 *)0
            ) != 0) &&
            ((pool->status & OPEN_CFW_CMSIS_POOL_OPS_STATUS) ==
             OPEN_CFW_CMSIS_POOL_OPS_STATUS)
        ) {
            mask = ulSetInterruptMask();
            block = open_cfw_cmsis_memory_pool_alloc_block(pool);
            if (block == (void *)0) {
                block = open_cfw_cmsis_memory_pool_create_block(pool);
            }
            vClearInterruptMask(mask);
        }
    } else if (
        open_cfw_freertos_queue_semaphore_take_upstream_candidate(
            pool->sem,
            timeout
        ) != 0
    ) {
        if ((pool->status & OPEN_CFW_CMSIS_POOL_OPS_STATUS) ==
            OPEN_CFW_CMSIS_POOL_OPS_STATUS) {
            open_cfw_freertos_port_enter_critical();
            block = open_cfw_cmsis_memory_pool_alloc_block(pool);
            if (block == (void *)0) {
                block = open_cfw_cmsis_memory_pool_create_block(pool);
            }
            open_cfw_freertos_port_exit_critical();
        }
    }
    return block;
}

__attribute__((used, noinline))
open_cfw_cmsis_pool_ops_int32 open_cfw_cmsis_memory_pool_free(
    void *pool_id,
    void *block
)
{
    open_cfw_cmsis_pool_ops_control *pool =
        (open_cfw_cmsis_pool_ops_control *)pool_id;
    open_cfw_cmsis_pool_ops_uint32 mask;
    open_cfw_cmsis_pool_ops_int32 yield;

    if ((pool == (open_cfw_cmsis_pool_ops_control *)0) ||
        (block == (void *)0)) {
        return OPEN_CFW_CMSIS_POOL_OPS_ERROR_PARAMETER;
    }
    if ((pool->status & OPEN_CFW_CMSIS_POOL_OPS_STATUS) !=
        OPEN_CFW_CMSIS_POOL_OPS_STATUS) {
        return OPEN_CFW_CMSIS_POOL_OPS_ERROR_RESOURCE;
    }
    if (
        ((open_cfw_cmsis_pool_ops_uintptr)block <
         (open_cfw_cmsis_pool_ops_uintptr)pool->mem_arr) ||
        ((open_cfw_cmsis_pool_ops_uintptr)block >
         (open_cfw_cmsis_pool_ops_uintptr)
         &pool->mem_arr[pool->mem_sz - 1U])
    ) {
        return OPEN_CFW_CMSIS_POOL_OPS_ERROR_PARAMETER;
    }

    if (open_cfw_cmsis_irq_context() != 0U) {
        if (
            open_cfw_freertos_queue_messages_waiting_from_isr(pool->sem) ==
            pool->bl_cnt
        ) {
            return OPEN_CFW_CMSIS_POOL_OPS_ERROR_RESOURCE;
        }
        mask = ulSetInterruptMask();
        open_cfw_cmsis_memory_pool_free_block(pool, block);
        vClearInterruptMask(mask);
        yield = 0;
        (void)open_cfw_freertos_queue_give_from_isr(pool->sem, &yield);
        if (yield != 0) {
            OPEN_CFW_CMSIS_POOL_OPS_PENDSV_SET();
        }
    } else {
        if (
            open_cfw_freertos_queue_messages_waiting(pool->sem) ==
            pool->bl_cnt
        ) {
            return OPEN_CFW_CMSIS_POOL_OPS_ERROR_RESOURCE;
        }
        open_cfw_freertos_port_enter_critical();
        open_cfw_cmsis_memory_pool_free_block(pool, block);
        open_cfw_freertos_port_exit_critical();
        (void)open_cfw_freertos_queue_generic_send(
            pool->sem,
            (const void *)0,
            0U,
            0
        );
    }
    return OPEN_CFW_CMSIS_POOL_OPS_OK;
}
