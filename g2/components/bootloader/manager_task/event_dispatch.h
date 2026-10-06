/* SPDX-License-Identifier: MIT. Recovered8-byte deferred-call queue format. */
#ifndef OPENCFW_BOOTLOADER_EVENT_DISPATCH_H
#define OPENCFW_BOOTLOADER_EVENT_DISPATCH_H
#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t argument, callback_address; } opencfw_boot_event_message;
_Static_assert(sizeof(opencfw_boot_event_message)==8,"ARM32 deferred call");
_Static_assert(offsetof(opencfw_boot_event_message,callback_address)==4,"callback offset");
void opencfw_boot_event_thread(void *argument);
void opencfw_boot_event_enqueue(uint32_t callback,uint32_t argument,uint32_t timeout);
void opencfw_boot_event_timer_callback(uint32_t argument);
#endif
