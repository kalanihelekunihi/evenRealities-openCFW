/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_DAEMON_H
#define OPENCFW_DAEMON_H
#include "../freertos_queue/queue.h"
/* Only zero-block-time receive and negative callback commands are supplied.
 * Coherent scheduler wait lists must be provided; group pointers are borrowed. */
BaseType_t opencfw_queue_receive_nowait(Queue_t *,void *);
void prvCopyDataFromQueue(Queue_t * const,void * const);
void opencfw_timer_callbacks_drain(void);
void opencfw_daemon_critical_enter(void);
void opencfw_daemon_critical_exit(void);
void opencfw_daemon_yield(void);
BaseType_t opencfw_daemon_scheduler_state(void);
void opencfw_daemon_positive_boundary(void) __attribute__((noreturn));
#endif
