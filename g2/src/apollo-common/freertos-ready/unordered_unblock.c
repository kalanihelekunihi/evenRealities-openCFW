/* SPDX-License-Identifier: MIT
 * Source projection of FreeRTOS V10.5.1 tasks.c
 * vTaskRemoveFromUnorderedEventList. The TCB/list prefix and scheduler RAM
 * addresses are the recovered Apollo Main ABI in ready_compat.h.
 */
#include "ready_compat.h"

void vTaskRemoveFromUnorderedEventList(ListItem_t *item, EventBits_t value)
{
    TCB_t *task;
    configASSERT(uxSchedulerSuspended != pdFALSE);
    configASSERT(item != NULL);

    item->xItemValue = value | 0x80000000u;
    task = (TCB_t *)item->pvOwner;
    configASSERT(task != NULL);
    listREMOVE_ITEM(item);

#if configUSE_TICKLESS_IDLE != 0
    if (listLIST_IS_EMPTY(pxDelayedTaskList) != pdFALSE) {
        xNextTaskUnblockTime = portMAX_DELAY;
    } else {
        xNextTaskUnblockTime = listGET_ITEM_VALUE_OF_HEAD_ENTRY(pxDelayedTaskList);
    }
#endif

    listREMOVE_ITEM(&task->xStateListItem);
    prvAddTaskToReadyList(task);
    if (task->uxPriority > pxCurrentTCB->uxPriority) {
        xYieldPending = pdTRUE;
    }
}
