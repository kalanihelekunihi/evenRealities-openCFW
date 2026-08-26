/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-routed reconstruction of the seven-function G2 Cordio WSF
 * message layer.  The function texts have an exact Apache-2.0 Packetcraft
 * source route at r19.02; the OpenCFW-local names are linked through guarded
 * production redirects.
 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_WSF_MSG_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_WSF_MSG_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_cordio_wsf_queue_candidate.h"

enum {
    OPEN_CFW_CORDIO_WSF_MESSAGE_QUEUE_EVENT = 0x01U
};

struct open_cfw_cordio_wsf_message_internal_candidate {
    struct open_cfw_cordio_wsf_message_internal_candidate *next;
    uint8_t handler_id;
};

void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint16_t length);
void open_cfw_cordio_wsf_buffer_free_candidate(void *buffer);
struct open_cfw_cordio_wsf_queue_candidate *
open_cfw_cordio_wsf_task_message_queue_candidate(uint8_t handler_id);
void open_cfw_cordio_wsf_task_set_ready_candidate(
    uint8_t handler_id,
    uint8_t event_mask
);

void *open_cfw_cordio_wsf_message_data_allocate_candidate(
    uint16_t length,
    uint8_t tailroom
);
void *open_cfw_cordio_wsf_message_allocate_candidate(uint16_t length);
void open_cfw_cordio_wsf_message_free_candidate(void *message);
void open_cfw_cordio_wsf_message_send_candidate(
    uint8_t handler_id,
    void *message
);
void open_cfw_cordio_wsf_message_enqueue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    uint8_t handler_id,
    void *message
);
void *open_cfw_cordio_wsf_message_dequeue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    uint8_t *handler_id
);
void *open_cfw_cordio_wsf_message_peek_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    uint8_t *handler_id
);

/* Adapters close the names already used by the reconstructed OS dispatcher. */
void *open_cfw_cordio_wsf_os_message_dequeue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    uint8_t *handler_id
);
void open_cfw_cordio_wsf_os_message_free_candidate(void *message);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(
    offsetof(struct open_cfw_cordio_wsf_message_internal_candidate, next)
        == 0x00U,
    "G2 WSF internal message next offset"
);
_Static_assert(
    offsetof(
        struct open_cfw_cordio_wsf_message_internal_candidate,
        handler_id
    ) == 0x04U,
    "G2 WSF internal message handler offset"
);
_Static_assert(
    sizeof(struct open_cfw_cordio_wsf_message_internal_candidate) == 0x08U,
    "G2 WSF internal message size"
);
#endif

#endif /* OPEN_CFW_RUNTIME_CORDIO_WSF_MSG_CANDIDATE_H */
