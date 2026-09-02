/*
 * SPDX-License-Identifier: BSD-3-Clause
 * Copyright (c) 2025, Ambiq Micro, Inc.
 *
 * Bounded Apollo510 am_hal_queue adaptation for the G2 bootloader ABI.
 * The complete BSD-3-Clause terms are retained in this component's NOTICE.
 */

typedef __UINT8_TYPE__ open_cfw_queue_u8;
typedef __UINT32_TYPE__ open_cfw_queue_u32;
typedef _Bool open_cfw_queue_bool;

typedef struct open_cfw_queue {
    volatile open_cfw_queue_u32 write_index;
    volatile open_cfw_queue_u32 read_index;
    volatile open_cfw_queue_u32 length;
    open_cfw_queue_u32 capacity;
    open_cfw_queue_u32 item_size;
    open_cfw_queue_u8 *data;
} open_cfw_queue;

#if !defined(OPEN_CFW_QUEUE_HOST_TEST)
_Static_assert(sizeof(open_cfw_queue) == 24U, "queue ABI changed");
_Static_assert(__builtin_offsetof(open_cfw_queue, write_index) == 0U,
    "queue write-index offset changed");
_Static_assert(__builtin_offsetof(open_cfw_queue, read_index) == 4U,
    "queue read-index offset changed");
_Static_assert(__builtin_offsetof(open_cfw_queue, length) == 8U,
    "queue length offset changed");
_Static_assert(__builtin_offsetof(open_cfw_queue, capacity) == 12U,
    "queue capacity offset changed");
_Static_assert(__builtin_offsetof(open_cfw_queue, item_size) == 16U,
    "queue item-size offset changed");
_Static_assert(__builtin_offsetof(open_cfw_queue, data) == 20U,
    "queue data offset changed");
#endif

#if defined(OPEN_CFW_QUEUE_HOST_TEST)
extern open_cfw_queue_u32 open_cfw_queue_host_critical_save(void);
extern void open_cfw_queue_host_critical_restore(open_cfw_queue_u32 token);
#define OPEN_CFW_QUEUE_CRITICAL_SAVE() open_cfw_queue_host_critical_save()
#define OPEN_CFW_QUEUE_CRITICAL_RESTORE(token) \
    open_cfw_queue_host_critical_restore(token)
#else
extern open_cfw_queue_u32 open_cfw_bootloader_critical_save_41b8ec(void);
#define OPEN_CFW_QUEUE_CRITICAL_SAVE() \
    open_cfw_bootloader_critical_save_41b8ec()
static __inline__ void
open_cfw_queue_critical_restore(open_cfw_queue_u32 token)
{
    __asm__ volatile("msr primask, %0" : : "r"(token) : "memory");
}
#define OPEN_CFW_QUEUE_CRITICAL_RESTORE(token) \
    open_cfw_queue_critical_restore(token)
#endif

__attribute__((used, noinline))
void
open_cfw_bootloader_queue_init_4275ea(open_cfw_queue *queue, void *data,
                                      open_cfw_queue_u32 item_size,
                                      open_cfw_queue_u32 array_size)
{
    queue->write_index = 0U;
    queue->read_index = 0U;
    queue->length = 0U;
    queue->capacity = array_size;
    queue->item_size = item_size;
    queue->data = (open_cfw_queue_u8 *)data;
}

__attribute__((used, noinline))
open_cfw_queue_bool
open_cfw_bootloader_queue_item_add_427602(open_cfw_queue *queue,
                                          const void *source,
                                          open_cfw_queue_u32 item_count)
{
    const open_cfw_queue_u8 *source_bytes =
        (const open_cfw_queue_u8 *)source;
    open_cfw_queue_u32 byte_count = item_count * queue->item_size;
    open_cfw_queue_u32 token = OPEN_CFW_QUEUE_CRITICAL_SAVE();
    open_cfw_queue_bool success = 0;

    if (queue->capacity - queue->length >= byte_count) {
        open_cfw_queue_u32 index;

        for (index = 0U; index < byte_count; ++index) {
            if (source != (const void *)0) {
                queue->data[queue->write_index] = source_bytes[index];
            }
            queue->write_index = (queue->write_index + 1U) % queue->capacity;
        }
        queue->length += byte_count;
        success = 1;
    }

    OPEN_CFW_QUEUE_CRITICAL_RESTORE(token);
    return success;
}

__attribute__((used, noinline))
open_cfw_queue_bool
open_cfw_bootloader_queue_item_get_427660(open_cfw_queue *queue, void *destination,
                                          open_cfw_queue_u32 item_count)
{
    open_cfw_queue_u8 *destination_bytes = (open_cfw_queue_u8 *)destination;
    open_cfw_queue_u32 byte_count = item_count * queue->item_size;
    open_cfw_queue_u32 token = OPEN_CFW_QUEUE_CRITICAL_SAVE();
    open_cfw_queue_bool success = 0;

    if (queue->length >= byte_count) {
        open_cfw_queue_u32 index;

        for (index = 0U; index < byte_count; ++index) {
            if (destination != (void *)0) {
                destination_bytes[index] = queue->data[queue->read_index];
            }
            queue->read_index = (queue->read_index + 1U) % queue->capacity;
        }
        queue->length -= byte_count;
        success = 1;
    }

    OPEN_CFW_QUEUE_CRITICAL_RESTORE(token);
    return success;
}
