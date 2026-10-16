#ifndef R1_NOTIFICATION_WRAPPER_CONTRACT_H
#define R1_NOTIFICATION_WRAPPER_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"
#include "event_groups.h"
#include "cmsis_os2.h"
_Static_assert(configTASK_NOTIFICATION_ARRAY_ENTRIES==1 && configUSE_OS2_THREAD_FLAGS==1 && configUSE_OS2_EVENTFLAGS_FROM_ISR==1,"native notification wrapper variant");
#endif
