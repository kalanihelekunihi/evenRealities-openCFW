/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-routed G2 WSF message reconstruction. Packetcraft r19.02
 * supplies an exact Apache-2.0 source route for the seven linked definitions.
 */

#include "runtime_cordio_wsf_msg_candidate.h"

#if !defined(OPEN_CFW_WSF_MSG_DATA_ALLOCATE_ONLY) && \
    !defined(OPEN_CFW_WSF_MSG_ALLOCATE_ONLY) && \
    !defined(OPEN_CFW_WSF_MSG_FREE_ONLY) && \
    !defined(OPEN_CFW_WSF_MSG_SEND_ONLY) && \
    !defined(OPEN_CFW_WSF_MSG_ENQUEUE_ONLY) && \
    !defined(OPEN_CFW_WSF_MSG_DEQUEUE_ONLY) && \
    !defined(OPEN_CFW_WSF_MSG_PEEK_ONLY)
#define OPEN_CFW_WSF_MSG_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_WSF_MSG_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_MSG_DATA_ALLOCATE_ONLY)
__attribute__((used, noinline))
void *open_cfw_cordio_wsf_message_data_allocate_candidate(
    uint16_t length,
    uint8_t tailroom
)
{
    return open_cfw_cordio_wsf_message_allocate_candidate(
        (uint16_t)(length + tailroom)
    );
}
#endif

#if defined(OPEN_CFW_WSF_MSG_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_MSG_ALLOCATE_ONLY)
__attribute__((used, noinline))
void *open_cfw_cordio_wsf_message_allocate_candidate(uint16_t length)
{
    struct open_cfw_cordio_wsf_message_internal_candidate *message =
        open_cfw_cordio_wsf_buffer_allocate_candidate(
            (uint16_t)(
                length
                + sizeof(struct open_cfw_cordio_wsf_message_internal_candidate)
            )
        );

    if (message != NULL) {
        message++;
    }
    return message;
}
#endif

#if defined(OPEN_CFW_WSF_MSG_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_MSG_FREE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_message_free_candidate(void *message)
{
    open_cfw_cordio_wsf_buffer_free_candidate(
        ((struct open_cfw_cordio_wsf_message_internal_candidate *)message) - 1
    );
}
#endif

#if defined(OPEN_CFW_WSF_MSG_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_MSG_SEND_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_message_send_candidate(
    uint8_t handler_id,
    void *message
)
{
    open_cfw_cordio_wsf_message_enqueue_candidate(
        open_cfw_cordio_wsf_task_message_queue_candidate(handler_id),
        handler_id,
        message
    );
    open_cfw_cordio_wsf_task_set_ready_candidate(
        handler_id,
        OPEN_CFW_CORDIO_WSF_MESSAGE_QUEUE_EVENT
    );
}
#endif

#if defined(OPEN_CFW_WSF_MSG_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_MSG_ENQUEUE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_message_enqueue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    uint8_t handler_id,
    void *message
)
{
    struct open_cfw_cordio_wsf_message_internal_candidate *internal =
        ((struct open_cfw_cordio_wsf_message_internal_candidate *)message) - 1;

    internal->handler_id = handler_id;
    open_cfw_cordio_wsf_queue_enqueue_candidate(queue, internal);
}
#endif

#if defined(OPEN_CFW_WSF_MSG_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_MSG_DEQUEUE_ONLY)
__attribute__((used, noinline))
void *open_cfw_cordio_wsf_message_dequeue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    uint8_t *handler_id
)
{
    struct open_cfw_cordio_wsf_message_internal_candidate *message =
        open_cfw_cordio_wsf_queue_dequeue_candidate(queue);

    if (message != NULL) {
        *handler_id = message->handler_id;
        message++;
    }
    return message;
}
#endif

#if defined(OPEN_CFW_WSF_MSG_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_MSG_PEEK_ONLY)
__attribute__((used, noinline))
void *open_cfw_cordio_wsf_message_peek_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    uint8_t *handler_id
)
{
    struct open_cfw_cordio_wsf_message_internal_candidate *message =
        queue->head;

    if (message != NULL) {
        *handler_id = message->handler_id;
        message++;
    }
    return message;
}
#endif

#ifdef OPEN_CFW_WSF_MSG_BUILD_ALL
void *open_cfw_cordio_wsf_os_message_dequeue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    uint8_t *handler_id
)
{
    return open_cfw_cordio_wsf_message_dequeue_candidate(queue, handler_id);
}

void open_cfw_cordio_wsf_os_message_free_candidate(void *message)
{
    open_cfw_cordio_wsf_message_free_candidate(message);
}
#endif
