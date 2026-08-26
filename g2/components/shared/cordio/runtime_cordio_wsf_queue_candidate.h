/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-routed clean-room ABI for the G2 Cordio WSF intrusive queue.
 * Every queued element stores its next pointer in its first machine word.
 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_WSF_QUEUE_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_WSF_QUEUE_CANDIDATE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

struct open_cfw_cordio_wsf_queue_candidate {
    void *head;
    void *tail;
};

void open_cfw_cordio_wsf_cs_enter_candidate(void);
void open_cfw_cordio_wsf_cs_exit_candidate(void);

void open_cfw_cordio_wsf_queue_enqueue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    void *element
);
void *open_cfw_cordio_wsf_queue_dequeue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue
);
void open_cfw_cordio_wsf_queue_push_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    void *element
);
void open_cfw_cordio_wsf_queue_insert_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    void *element,
    void *previous
);
void open_cfw_cordio_wsf_queue_remove_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    void *element,
    void *previous
);
uint16_t open_cfw_cordio_wsf_queue_count_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue
);
bool open_cfw_cordio_wsf_queue_empty_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue
);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_queue_candidate, head) == 0x00U,
    "G2 WSF queue head offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_queue_candidate, tail) == 0x04U,
    "G2 WSF queue tail offset"
);
_Static_assert(
    sizeof(struct open_cfw_cordio_wsf_queue_candidate) == 0x08U,
    "G2 WSF queue size"
);
#endif

#endif /* OPEN_CFW_RUNTIME_CORDIO_WSF_QUEUE_CANDIDATE_H */
