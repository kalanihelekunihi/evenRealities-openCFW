#ifndef R1_NATIVE_TASK_SUSPEND_H
#define R1_NATIVE_TASK_SUSPEND_H
#include <stdint.h>
#include "cmsis_os2.h"
/* Existing shared owner in board/native_sync.c, stock context + 28. */
extern osEventFlagsId_t volatile r1_native_sync_event_flags;
void r1_task_suspend_handshake(osThreadId_t worker,uint32_t ordinal);
#endif
