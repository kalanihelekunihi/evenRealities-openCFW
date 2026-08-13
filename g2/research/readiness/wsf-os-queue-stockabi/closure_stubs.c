#include <stddef.h>
#include <stdint.h>
#include "wsf_types.h"
#include "wsf_os.h"
#include "wsf_queue.h"
#include "wsf_msg.h"
#include "wsf_timer.h"
#include "wsf_cs.h"
#include "FreeRTOS.h"
#include "event_groups.h"

void WsfSetOsSpecificEvent(void);

void *memset(void *destination, int value, size_t length)
{
    unsigned char *bytes = destination;
    while (length-- != 0U) { *bytes++ = (unsigned char)value; }
    return destination;
}
void *WsfMsgDeq(wsfQueue_t *queue, wsfHandlerId_t *handler_id)
{ (void)queue; (void)handler_id; return NULL; }
void WsfMsgFree(void *message) { (void)message; }
wsfTimer_t *WsfTimerServiceExpired(wsfTaskId_t task_id)
{ (void)task_id; return NULL; }
void WsfTimerUpdateTicks(void) {}
BaseType_t xPortIsInsideInterrupt(void) { return pdFALSE; }
void vPortYield(void) {}
EventGroupHandle_t xEventGroupCreate(void) { return (EventGroupHandle_t)1; }
BaseType_t xEventGroupSetBitsFromISR(EventGroupHandle_t group, EventBits_t bits,
                                    BaseType_t *woken)
{ (void)group; (void)bits; (void)woken; return pdPASS; }
EventBits_t xEventGroupSetBits(EventGroupHandle_t group, EventBits_t bits)
{ (void)group; return bits; }
EventBits_t xEventGroupWaitBits(EventGroupHandle_t group, EventBits_t bits,
                               BaseType_t clear, BaseType_t all,
                               TickType_t ticks)
{ (void)group; (void)clear; (void)all; (void)ticks; return bits; }

static unsigned char queue_elements[2][4];
static wsfQueue_t closure_queue;
static wsfTimer_t closure_timer;
static void closure_handler(wsfEventMask_t event, wsfMsgHdr_t *message)
{ (void)event; (void)message; }

void open_cfw_wsf_stockabi_closure_root(void)
{
    void *item;
    WsfCsEnter(); WsfCsExit(); WsfTaskLock(); WsfTaskUnlock();
    WsfSetOsSpecificEvent(); WsfSetEvent(0, 1); WsfTaskSetReady(0, 1);
    (void)WsfTaskMsgQueue(0); (void)WsfOsSetNextHandler(closure_handler);
    (void)wsfOsReadyToSleep(); WsfOsInit(); wsfOsDispatcher();
    WsfQueueEnq(&closure_queue, queue_elements[0]);
    item = WsfQueueDeq(&closure_queue); (void)item;
    WsfQueuePush(&closure_queue, queue_elements[0]);
    WsfQueueInsert(&closure_queue, queue_elements[1], queue_elements[0]);
    WsfQueueRemove(&closure_queue, queue_elements[1], queue_elements[0]);
    (void)WsfQueueCount(&closure_queue); (void)WsfQueueEmpty(&closure_queue);
    (void)closure_timer;
}
