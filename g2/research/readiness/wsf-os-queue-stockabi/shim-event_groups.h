#ifndef OPENCFW_SCRATCH_EVENT_GROUPS_H
#define OPENCFW_SCRATCH_EVENT_GROUPS_H

#include "FreeRTOS.h"

typedef void *EventGroupHandle_t;

EventGroupHandle_t xEventGroupCreate(void);
BaseType_t xEventGroupSetBitsFromISR(
    EventGroupHandle_t group,
    EventBits_t bits,
    BaseType_t *higher_priority_task_woken
);
EventBits_t xEventGroupSetBits(EventGroupHandle_t group, EventBits_t bits);
EventBits_t xEventGroupWaitBits(
    EventGroupHandle_t group,
    EventBits_t bits,
    BaseType_t clear_on_exit,
    BaseType_t wait_for_all,
    TickType_t wait_ticks
);

#endif
