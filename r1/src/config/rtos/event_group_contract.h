#ifndef R1_EVENT_GROUP_CONTRACT_H
#define R1_EVENT_GROUP_CONTRACT_H
#include "FreeRTOS.h"
#include "event_groups.h"
#include "timers.h"
_Static_assert(sizeof(StaticEventGroup_t)==32 && sizeof(EventBits_t)==4,"native event-group configuration");
void vPortValidateInterruptPriority(void);
#undef portASSERT_IF_INTERRUPT_PRIORITY_INVALID
#define portASSERT_IF_INTERRUPT_PRIORITY_INVALID() vPortValidateInterruptPriority()
#endif
