/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include "lvp_app_core.h"
#include "lvp_queue.h"
/* Stock initialization passes 64 bytes, eight-byte members and these two
 * separate BSS objects. The pinned SDK declares an eight-event misc queue. */
unsigned char s_app_misc_event_queue_buffer[8 * sizeof(APP_EVENT)];
LVP_QUEUE s_app_misc_event_queue;
_Static_assert(sizeof(APP_EVENT)==8,"event width");
_Static_assert(sizeof(LVP_QUEUE)==20,"queue descriptor width");
_Static_assert(offsetof(LVP_QUEUE,buffer)==8,"queue buffer offset");
_Static_assert(offsetof(LVP_QUEUE,member_size)==16,"queue record-size offset");
