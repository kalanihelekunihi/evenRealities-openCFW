#ifndef R1_TIMER_NEW_CONTRACT_H
#define R1_TIMER_NEW_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"
#include "cmsis_os2.h"
_Static_assert(sizeof(StaticTimer_t)==44 && sizeof(osTimerAttr_t)==16,"native CMSIS timer creation layout");
#endif
