/* SPDX-License-Identifier: MIT */
/* Bounded reconstruction of the pinned FreeRTOS V10.5.1 nonblocking receive
 * and negative timer-command paths. Positive timers and blocking are external. */
#include "daemon.h"
#include <stddef.h>
#define ASSERT(x) do{if(!(x))opencfw_event_group_assert_failure();}while(0)
BaseType_t opencfw_queue_receive_nowait(Queue_t *q,void *buffer)
{
    ASSERT(q);ASSERT(buffer || q->uxItemSize==0);
    (void)opencfw_daemon_scheduler_state(); /* Stock queries even with wait=0. */
    opencfw_daemon_critical_enter();
    UBaseType_t waiting=q->uxMessagesWaiting;
    if(waiting==0){opencfw_daemon_critical_exit();return 0;}
    prvCopyDataFromQueue(q,buffer);
    q->uxMessagesWaiting=waiting-1;
    if(q->xTasksWaitingToSend.uxNumberOfItems!=0 &&
       xTaskRemoveFromEventList(&q->xTasksWaitingToSend)!=0)
        opencfw_daemon_yield();
    opencfw_daemon_critical_exit();
    return 1;
}
void opencfw_timer_callbacks_drain(void)
{
    struct {int32_t command;PendedFunction_t callback;void *group;uint32_t bits;} m;
    _Static_assert(sizeof(m)==16,"stock daemon stack copy");
    while(opencfw_queue_receive_nowait(*(Queue_t **)(uintptr_t)0x20074ab0u,&m)!=0){
        if(m.command<0)m.callback(m.group,m.bits);
        else opencfw_daemon_positive_boundary();
    }
}
