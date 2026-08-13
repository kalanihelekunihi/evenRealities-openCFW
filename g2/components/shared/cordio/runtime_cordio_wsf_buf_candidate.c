/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room behavioral reconstruction of the G2 Cordio
 * WSF buffer-pool implementation. Proprietary upstream text is not copied.
 */

#include "runtime_cordio_wsf_buf_candidate.h"

#include <stdbool.h>

static uintptr_t open_cfw_cordio_wsf_buffer_end_candidate(
    uint16_t memory_length
)
{
    return (uintptr_t)open_cfw_cordio_wsf_buffer_memory_candidate
        + ((uint16_t)(memory_length / OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT)
            * OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT);
}

uint16_t open_cfw_cordio_wsf_buffer_init_candidate(
    uint16_t memory_length,
    uint8_t *memory,
    uint8_t pool_count,
    const struct open_cfw_cordio_wsf_buffer_pool_descriptor_candidate
        *descriptors
)
{
    struct open_cfw_cordio_wsf_buffer_pool_candidate *pool;
    struct open_cfw_cordio_wsf_buffer_block_candidate *start;
    uintptr_t end;
    uint16_t units;
    uint16_t requested_length;
    uint8_t remaining;
    uint8_t buffers;

    open_cfw_cordio_wsf_buffer_memory_candidate =
        (struct open_cfw_cordio_wsf_buffer_block_candidate *)memory;
    pool = (struct open_cfw_cordio_wsf_buffer_pool_candidate *)memory;
    start = (struct open_cfw_cordio_wsf_buffer_block_candidate *)(
        pool + pool_count
    );
    open_cfw_cordio_wsf_buffer_pool_count_candidate = pool_count;
    remaining = pool_count;
    end = open_cfw_cordio_wsf_buffer_end_candidate(memory_length);

    for (;;) {
        if ((uintptr_t)start > end) {
            return 0U;
        }
        if (remaining-- == 0U) {
            break;
        }

        requested_length = descriptors->length;
        if (requested_length < OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT) {
            pool->descriptor.length = OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT;
        } else {
            pool->descriptor.length = (uint16_t)(
                (requested_length
                    + (OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT - 1U))
                & ~(OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT - 1U)
            );
        }
        pool->descriptor.count = descriptors->count;
        descriptors++;
        pool->start = start;
        pool->free = start;

        units = (uint16_t)(
            pool->descriptor.length / OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT
        );
        buffers = pool->descriptor.count;
        while (buffers > 1U) {
            if ((uintptr_t)start > end) {
                return 0U;
            }
            start->next = start + units;
            start += units;
            buffers--;
        }
        if ((uintptr_t)start > end) {
            return 0U;
        }
        start->next = NULL;
        start += units;
        pool++;
    }

    open_cfw_cordio_wsf_buffer_memory_length_candidate = (uint16_t)(
        (uintptr_t)start
        - (uintptr_t)open_cfw_cordio_wsf_buffer_memory_candidate
    );
    return open_cfw_cordio_wsf_buffer_memory_length_candidate;
}

void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint16_t length)
{
    struct open_cfw_cordio_wsf_buffer_pool_candidate *pool =
        (struct open_cfw_cordio_wsf_buffer_pool_candidate *)
            open_cfw_cordio_wsf_buffer_memory_candidate;
    struct open_cfw_cordio_wsf_buffer_block_candidate *buffer;
    uint8_t remaining = open_cfw_cordio_wsf_buffer_pool_count_candidate;

    while (remaining > 0U) {
        if (length <= pool->descriptor.length) {
            open_cfw_cordio_wsf_cs_enter_candidate();
            buffer = pool->free;
            if (buffer != NULL) {
                pool->free = buffer->next;
                buffer->free_marker = 0U;
                open_cfw_cordio_wsf_cs_exit_candidate();
                return buffer;
            }
            open_cfw_cordio_wsf_cs_exit_candidate();
        }
        pool++;
        remaining--;
    }

    open_cfw_cordio_wsf_buffer_allocation_failure_candidate(length);
    return NULL;
}

void open_cfw_cordio_wsf_buffer_free_candidate(void *buffer)
{
    struct open_cfw_cordio_wsf_buffer_pool_candidate *pool =
        (struct open_cfw_cordio_wsf_buffer_pool_candidate *)
            open_cfw_cordio_wsf_buffer_memory_candidate;
    struct open_cfw_cordio_wsf_buffer_block_candidate *block = buffer;
    uint8_t remaining = open_cfw_cordio_wsf_buffer_pool_count_candidate;

    pool += remaining;
    while (remaining > 0U) {
        pool--;
        if ((uintptr_t)block >= (uintptr_t)pool->start) {
            open_cfw_cordio_wsf_cs_enter_candidate();
            block->free_marker = OPEN_CFW_CORDIO_WSF_BUFFER_FREE_MARKER;
            block->next = pool->free;
            pool->free = block;
            open_cfw_cordio_wsf_cs_exit_candidate();
            return;
        }
        remaining--;
    }
}

uint8_t *open_cfw_cordio_wsf_buffer_allocation_stats_candidate(void)
{
    return NULL;
}

uint8_t open_cfw_cordio_wsf_buffer_number_of_pools_candidate(void)
{
    return open_cfw_cordio_wsf_buffer_pool_count_candidate;
}

void open_cfw_cordio_wsf_buffer_pool_stats_candidate(
    struct open_cfw_cordio_wsf_buffer_pool_stats_candidate *stats,
    uint8_t pool_id
)
{
    struct open_cfw_cordio_wsf_buffer_pool_candidate *pools =
        (struct open_cfw_cordio_wsf_buffer_pool_candidate *)
            open_cfw_cordio_wsf_buffer_memory_candidate;

    if (pool_id >= open_cfw_cordio_wsf_buffer_pool_count_candidate) {
        stats->buffer_size = 0U;
        return;
    }
    open_cfw_cordio_wsf_cs_enter_candidate();
    stats->buffer_size = pools[pool_id].descriptor.length;
    stats->number_of_buffers = pools[pool_id].descriptor.count;
    stats->allocated = 0U;
    stats->maximum_allocated = 0U;
    stats->maximum_request_length = 0U;
    open_cfw_cordio_wsf_cs_exit_candidate();
}

void open_cfw_cordio_wsf_buffer_diagnostics_register_candidate(
    void (*callback)(void *information)
)
{
    (void)callback;
}
