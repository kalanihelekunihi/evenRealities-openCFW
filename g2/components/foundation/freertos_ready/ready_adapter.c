/* SPDX-License-Identifier: MIT */
#include "../freertos_queue/queue.h"
#include "ready.h"
/* Preserve existing caller ABI without altering earlier fixture modules. */
BaseType_t xTaskRemoveFromEventList(List_t *list)
{return opencfw_ready_remove_event_list(list);}
