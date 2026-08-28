/*
 * SPDX-License-Identifier: MIT
 *
 * Production-routed clean-room behavioral reconstruction of the six linked
 * G2 Cordio WSF intrusive-queue functions.
 */

#include "runtime_cordio_wsf_queue_candidate.h"

#if !defined(OPEN_CFW_WSF_QUEUE_ENQUEUE_ONLY) && \
    !defined(OPEN_CFW_WSF_QUEUE_DEQUEUE_ONLY) && \
    !defined(OPEN_CFW_WSF_QUEUE_PUSH_ONLY) && \
    !defined(OPEN_CFW_WSF_QUEUE_INSERT_ONLY) && \
    !defined(OPEN_CFW_WSF_QUEUE_REMOVE_ONLY) && \
    !defined(OPEN_CFW_WSF_QUEUE_COUNT_ONLY)
#define OPEN_CFW_WSF_QUEUE_BUILD_ALL 1
#endif

static void **open_cfw_cordio_wsf_queue_next_candidate(void *element)
{
    return (void **)element;
}

#if defined(OPEN_CFW_WSF_QUEUE_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_QUEUE_ENQUEUE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_queue_enqueue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    void *element
)
{
    *open_cfw_cordio_wsf_queue_next_candidate(element) = NULL;

    open_cfw_cordio_wsf_cs_enter_candidate();
    if (queue->head == NULL) {
        queue->head = element;
        queue->tail = element;
    } else {
        *open_cfw_cordio_wsf_queue_next_candidate(queue->tail) = element;
        queue->tail = element;
    }
    open_cfw_cordio_wsf_cs_exit_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_QUEUE_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_QUEUE_DEQUEUE_ONLY)
__attribute__((used, noinline))
void *open_cfw_cordio_wsf_queue_dequeue_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue
)
{
    void *element;

    open_cfw_cordio_wsf_cs_enter_candidate();
    element = queue->head;
    if (element != NULL) {
        queue->head = *open_cfw_cordio_wsf_queue_next_candidate(element);
        if (queue->head == NULL) {
            queue->tail = NULL;
        }
    }
    open_cfw_cordio_wsf_cs_exit_candidate();
    return element;
}
#endif

#if defined(OPEN_CFW_WSF_QUEUE_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_QUEUE_PUSH_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_queue_push_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    void *element
)
{
    open_cfw_cordio_wsf_cs_enter_candidate();
    *open_cfw_cordio_wsf_queue_next_candidate(element) = queue->head;
    if (queue->head == NULL) {
        queue->tail = element;
    }
    queue->head = element;
    open_cfw_cordio_wsf_cs_exit_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_QUEUE_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_QUEUE_INSERT_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_queue_insert_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    void *element,
    void *previous
)
{
    open_cfw_cordio_wsf_cs_enter_candidate();
    if ((queue->head == NULL) || (previous == queue->tail)) {
        open_cfw_cordio_wsf_queue_enqueue_candidate(queue, element);
    } else if (previous == NULL) {
        open_cfw_cordio_wsf_queue_push_candidate(queue, element);
    } else {
        *open_cfw_cordio_wsf_queue_next_candidate(element) =
            *open_cfw_cordio_wsf_queue_next_candidate(previous);
        *open_cfw_cordio_wsf_queue_next_candidate(previous) = element;
    }
    open_cfw_cordio_wsf_cs_exit_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_QUEUE_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_QUEUE_REMOVE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wsf_queue_remove_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue,
    void *element,
    void *previous
)
{
    open_cfw_cordio_wsf_cs_enter_candidate();
    if (element == queue->head) {
        queue->head = *open_cfw_cordio_wsf_queue_next_candidate(element);
    } else if (previous != NULL) {
        *open_cfw_cordio_wsf_queue_next_candidate(previous) =
            *open_cfw_cordio_wsf_queue_next_candidate(element);
    }
    if (element == queue->tail) {
        queue->tail = previous;
    }
    open_cfw_cordio_wsf_cs_exit_candidate();
}
#endif

#if defined(OPEN_CFW_WSF_QUEUE_BUILD_ALL) || \
    defined(OPEN_CFW_WSF_QUEUE_COUNT_ONLY)
__attribute__((used, noinline))
uint16_t open_cfw_cordio_wsf_queue_count_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue
)
{
    uint16_t count = 0U;
    void *element;

    open_cfw_cordio_wsf_cs_enter_candidate();
    for (element = queue->head; element != NULL;
         element = *open_cfw_cordio_wsf_queue_next_candidate(element)) {
        count++;
    }
    open_cfw_cordio_wsf_cs_exit_candidate();
    return count;
}
#endif

#ifdef OPEN_CFW_WSF_QUEUE_BUILD_ALL
bool open_cfw_cordio_wsf_queue_empty_candidate(
    struct open_cfw_cordio_wsf_queue_candidate *queue
)
{
    bool empty;

    open_cfw_cordio_wsf_cs_enter_candidate();
    empty = queue->head == NULL;
    open_cfw_cordio_wsf_cs_exit_candidate();
    return empty;
}
#endif
