/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_READY_H
#define OPENCFW_READY_H
#include "../freertos_event_group/event_group.h"
/* Only the accessed prefix is represented; not a complete allocated TCB. */
typedef struct {void *pxTopOfStack;ListItem_t xStateListItem,xEventListItem;UBaseType_t uxPriority;} TCB_t;
BaseType_t opencfw_ready_remove_event_list(const List_t * const);
UBaseType_t uxTaskGetNumberOfTasks(void);
void vListInsertEnd(List_t * const,ListItem_t * const);
UBaseType_t uxListRemove(ListItem_t * const);
#endif
