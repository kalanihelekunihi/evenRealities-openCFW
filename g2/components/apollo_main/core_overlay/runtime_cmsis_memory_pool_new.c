/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded, freestanding adapter for CMSIS-FreeRTOS v10.5.1
 * osMemoryPoolNew() at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 */

typedef __UINT8_TYPE__ open_cfw_cmsis_mpool_uint8;
typedef __UINT32_TYPE__ open_cfw_cmsis_mpool_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_mpool_int32;

typedef struct {
    const char *name;
    open_cfw_cmsis_mpool_uint32 attr_bits;
    void *cb_mem;
    open_cfw_cmsis_mpool_uint32 cb_size;
    void *mp_mem;
    open_cfw_cmsis_mpool_uint32 mp_size;
} open_cfw_cmsis_mpool_attr;

typedef struct open_cfw_cmsis_mpool_block {
    struct open_cfw_cmsis_mpool_block *next;
} open_cfw_cmsis_mpool_block;

typedef struct {
    open_cfw_cmsis_mpool_block *head;
    void *sem;
    open_cfw_cmsis_mpool_uint8 *mem_arr;
    open_cfw_cmsis_mpool_uint32 mem_sz;
    const char *name;
    open_cfw_cmsis_mpool_uint32 bl_sz;
    open_cfw_cmsis_mpool_uint32 bl_cnt;
    open_cfw_cmsis_mpool_uint32 n;
    volatile open_cfw_cmsis_mpool_uint32 status;
    open_cfw_cmsis_mpool_uint32 static_semaphore_words[20];
} open_cfw_cmsis_mpool_control;

enum {
    OPEN_CFW_CMSIS_MPOOL_CONTROL_SIZE = 0x74U,
    OPEN_CFW_CMSIS_MPOOL_STATUS = 0x5EED0000U
};

#if __SIZEOF_POINTER__ == 4
_Static_assert(
    sizeof(open_cfw_cmsis_mpool_attr) == 0x18U,
    "G2 osMemoryPoolAttr_t ABI must remain 24 bytes"
);
_Static_assert(
    sizeof(open_cfw_cmsis_mpool_control) ==
        OPEN_CFW_CMSIS_MPOOL_CONTROL_SIZE,
    "G2 MemPool_t ABI must remain 116 bytes"
);
_Static_assert(
    __builtin_offsetof(open_cfw_cmsis_mpool_control, static_semaphore_words)
        == 0x24U,
    "G2 embedded StaticSemaphore_t offset drift"
);
#endif

extern open_cfw_cmsis_mpool_uint32 open_cfw_cmsis_irq_context(void);
extern void *open_cfw_freertos_heap4_malloc(
    open_cfw_cmsis_mpool_uint32 size
);
extern void open_cfw_freertos_heap4_free(void *memory);
extern void *open_cfw_freertos_queue_create_counting_semaphore_static(
    open_cfw_cmsis_mpool_uint32 maximum_count,
    open_cfw_cmsis_mpool_uint32 initial_count,
    void *static_queue
);

__attribute__((used, noinline))
void *open_cfw_cmsis_memory_pool_new(
    open_cfw_cmsis_mpool_uint32 block_count,
    open_cfw_cmsis_mpool_uint32 block_size,
    const open_cfw_cmsis_mpool_attr *attr
)
{
    open_cfw_cmsis_mpool_control *pool;
    const char *name;
    open_cfw_cmsis_mpool_int32 control_mode;
    open_cfw_cmsis_mpool_int32 array_mode;
    open_cfw_cmsis_mpool_uint32 array_size;

    if (
        (open_cfw_cmsis_irq_context() != 0U) ||
        (block_count == 0U) ||
        (block_size == 0U)
    ) {
        return (void *)0;
    }

    pool = (open_cfw_cmsis_mpool_control *)0;
    array_size = (((block_size + 3U) >> 2U) * block_count) << 2U;
    name = (const char *)0;
    control_mode = -1;
    array_mode = -1;

    if (attr != (const open_cfw_cmsis_mpool_attr *)0) {
        if (attr->name != (const char *)0) {
            name = attr->name;
        }
        if (
            (attr->cb_mem != (void *)0) &&
            (attr->cb_size >= OPEN_CFW_CMSIS_MPOOL_CONTROL_SIZE)
        ) {
            control_mode = 1;
        } else if (
            (attr->cb_mem == (void *)0) &&
            (attr->cb_size == 0U)
        ) {
            control_mode = 0;
        }

        if (
            (attr->mp_mem == (void *)0) &&
            (attr->mp_size == 0U)
        ) {
            array_mode = 0;
        } else if (
            (attr->mp_mem != (void *)0) &&
            (((__UINTPTR_TYPE__)attr->mp_mem & 3U) == 0U) &&
            (attr->mp_size >= array_size)
        ) {
            array_mode = 1;
        }
    } else {
        control_mode = 0;
        array_mode = 0;
    }

    if (control_mode == 0) {
        pool = (open_cfw_cmsis_mpool_control *)
            open_cfw_freertos_heap4_malloc(
                OPEN_CFW_CMSIS_MPOOL_CONTROL_SIZE
            );
    } else if (attr != (const open_cfw_cmsis_mpool_attr *)0) {
        /* Preserve the selected v10.5.1 behavior for mode -1. */
        pool = (open_cfw_cmsis_mpool_control *)attr->cb_mem;
    }

    if (pool != (open_cfw_cmsis_mpool_control *)0) {
        pool->sem = open_cfw_freertos_queue_create_counting_semaphore_static(
            block_count,
            block_count,
            (void *)pool->static_semaphore_words
        );
        if (pool->sem != (void *)0) {
            if (array_mode == 0) {
                pool->mem_arr = (open_cfw_cmsis_mpool_uint8 *)
                    open_cfw_freertos_heap4_malloc(array_size);
            } else if (attr != (const open_cfw_cmsis_mpool_attr *)0) {
                /* Preserve the selected v10.5.1 behavior for mode -1. */
                pool->mem_arr =
                    (open_cfw_cmsis_mpool_uint8 *)attr->mp_mem;
            }
        }
    }

    if (
        (pool != (open_cfw_cmsis_mpool_control *)0) &&
        (pool->mem_arr != (open_cfw_cmsis_mpool_uint8 *)0)
    ) {
        pool->head = (open_cfw_cmsis_mpool_block *)0;
        pool->mem_sz = array_size;
        pool->name = name;
        pool->bl_sz = block_size;
        pool->bl_cnt = block_count;
        pool->n = 0U;
        pool->status = OPEN_CFW_CMSIS_MPOOL_STATUS;
        if (control_mode == 0) {
            pool->status |= 1U;
        }
        if (array_mode == 0) {
            pool->status |= 2U;
        }
    } else {
        if (
            (control_mode == 0) &&
            (pool != (open_cfw_cmsis_mpool_control *)0)
        ) {
            open_cfw_freertos_heap4_free(pool);
        }
        pool = (open_cfw_cmsis_mpool_control *)0;
    }

    return pool;
}
