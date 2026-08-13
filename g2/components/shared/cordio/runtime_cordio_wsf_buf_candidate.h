/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room ABI for the G2 Cordio WSF buffer pools.
 * Restricted vendor source is used only as a provenance/behavior oracle.
 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_WSF_BUF_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_WSF_BUF_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_CORDIO_WSF_BUFFER_FREE_MARKER = 0xFAABD00DU
};

struct open_cfw_cordio_wsf_buffer_pool_descriptor_candidate {
    uint16_t length;
    uint8_t count;
    uint8_t reserved;
};

struct open_cfw_cordio_wsf_buffer_block_candidate {
    struct open_cfw_cordio_wsf_buffer_block_candidate *next;
    uint32_t free_marker;
};

#define OPEN_CFW_CORDIO_WSF_BUFFER_ALIGNMENT \
    ((uint16_t)sizeof(struct open_cfw_cordio_wsf_buffer_block_candidate))

struct open_cfw_cordio_wsf_buffer_pool_candidate {
    struct open_cfw_cordio_wsf_buffer_pool_descriptor_candidate descriptor;
    struct open_cfw_cordio_wsf_buffer_block_candidate *start;
    struct open_cfw_cordio_wsf_buffer_block_candidate *free;
};

struct open_cfw_cordio_wsf_buffer_pool_stats_candidate {
    uint16_t buffer_size;
    uint8_t number_of_buffers;
    uint8_t allocated;
    uint8_t maximum_allocated;
    uint8_t reserved;
    uint16_t maximum_request_length;
};

extern struct open_cfw_cordio_wsf_buffer_block_candidate
    *open_cfw_cordio_wsf_buffer_memory_candidate;
extern uint16_t open_cfw_cordio_wsf_buffer_memory_length_candidate;
extern uint8_t open_cfw_cordio_wsf_buffer_pool_count_candidate;

void open_cfw_cordio_wsf_cs_enter_candidate(void);
void open_cfw_cordio_wsf_cs_exit_candidate(void);
void open_cfw_cordio_wsf_buffer_allocation_failure_candidate(uint16_t length);

uint16_t open_cfw_cordio_wsf_buffer_init_candidate(
    uint16_t memory_length,
    uint8_t *memory,
    uint8_t pool_count,
    const struct open_cfw_cordio_wsf_buffer_pool_descriptor_candidate
        *descriptors
);
void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint16_t length);
void open_cfw_cordio_wsf_buffer_free_candidate(void *buffer);

/* Source-family API completeness; no separate linked stock bodies are proven. */
uint8_t *open_cfw_cordio_wsf_buffer_allocation_stats_candidate(void);
uint8_t open_cfw_cordio_wsf_buffer_number_of_pools_candidate(void);
void open_cfw_cordio_wsf_buffer_pool_stats_candidate(
    struct open_cfw_cordio_wsf_buffer_pool_stats_candidate *stats,
    uint8_t pool_id
);
void open_cfw_cordio_wsf_buffer_diagnostics_register_candidate(
    void (*callback)(void *information)
);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(
    sizeof(struct open_cfw_cordio_wsf_buffer_pool_descriptor_candidate) == 4U,
    "G2 WSF buffer pool descriptor size"
);
_Static_assert(
    offsetof(
        struct open_cfw_cordio_wsf_buffer_pool_descriptor_candidate,
        count
    ) == 2U,
    "G2 WSF buffer pool count offset"
);
_Static_assert(
    sizeof(struct open_cfw_cordio_wsf_buffer_block_candidate) == 8U,
    "G2 WSF buffer block size"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_buffer_block_candidate, free_marker)
        == 4U,
    "G2 WSF buffer free-marker offset"
);
_Static_assert(
    sizeof(struct open_cfw_cordio_wsf_buffer_pool_candidate) == 12U,
    "G2 WSF internal pool size"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_buffer_pool_candidate, start) == 4U,
    "G2 WSF pool start offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_buffer_pool_candidate, free) == 8U,
    "G2 WSF pool free-list offset"
);
#endif

#endif /* OPEN_CFW_RUNTIME_CORDIO_WSF_BUF_CANDIDATE_H */
