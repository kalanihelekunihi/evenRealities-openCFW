/* --------------------------------------------------------------------------
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 *      Name:    cmsis_os2.c
 *      Purpose: CMSIS RTOS2 wrapper for FreeRTOS
 *
 *---------------------------------------------------------------------------*/
#include "notification_wrapper_contract.h"
#define EVENT_FLAGS_INVALID_BITS  (~((1UL << MAX_BITS_EVENT_GROUPS) - 1U))

#define THREAD_FLAGS_INVALID_BITS (~((1UL << MAX_BITS_TASK_NOTIFY)  - 1U))

#define MAX_BITS_EVENT_GROUPS     24U

#define MAX_BITS_TASK_NOTIFY      31U

#define IS_IRQ_MODE()             (__get_IPSR() != 0U)

#define IS_IRQ_MASKED()           ((__get_PRIMASK() != 0U) || (__get_BASEPRI() != 0U))

__STATIC_INLINE uint32_t IRQ_Context (void) {
  uint32_t irq;
  BaseType_t state;

  irq = 0U;

  if (IS_IRQ_MODE()) {
    /* Called from interrupt context */
    irq = 1U;
  }
  else {
    /* Get FreeRTOS scheduler state */
    state = xTaskGetSchedulerState();

    if (state != taskSCHEDULER_NOT_STARTED) {
      /* Scheduler was started */
      if (IS_IRQ_MASKED()) {
        /* Interrupts are masked */
        irq = 1U;
      }
    }
  }

  /* Return context, 0: thread context, 1: IRQ context */
  return (irq);
}

uint32_t osThreadFlagsSet (osThreadId_t thread_id, uint32_t flags) {
  TaskHandle_t hTask = (TaskHandle_t)thread_id;
  uint32_t rflags;
  BaseType_t yield;

  if ((hTask == NULL) || ((flags & THREAD_FLAGS_INVALID_BITS) != 0U)) {
    rflags = (uint32_t)osErrorParameter;
  }
  else {
    rflags = (uint32_t)osError;

    if (IRQ_Context() != 0U) {
      yield = pdFALSE;

      (void)xTaskNotifyFromISR (hTask, flags, eSetBits, &yield);
      (void)xTaskNotifyAndQueryFromISR (hTask, 0, eNoAction, &rflags, NULL);

      portYIELD_FROM_ISR (yield);
    }
    else {
      (void)xTaskNotify (hTask, flags, eSetBits);
      (void)xTaskNotifyAndQuery (hTask, 0, eNoAction, &rflags);
    }
  }
  /* Return flags after setting */
  return (rflags);
}

uint32_t osThreadFlagsWait (uint32_t flags, uint32_t options, uint32_t timeout) {
  uint32_t rflags, nval;
  uint32_t clear;
  TickType_t t0, td, tout;
  BaseType_t rval;

  if (IRQ_Context() != 0U) {
    rflags = (uint32_t)osErrorISR;
  }
  else if ((flags & THREAD_FLAGS_INVALID_BITS) != 0U) {
    rflags = (uint32_t)osErrorParameter;
  }
  else {
    if ((options & osFlagsNoClear) == osFlagsNoClear) {
      clear = 0U;
    } else {
      clear = flags;
    }

    rflags = 0U;
    tout   = timeout;

    t0 = xTaskGetTickCount();
    do {
      rval = xTaskNotifyWait (0, clear, &nval, tout);

      if (rval == pdPASS) {
        rflags &= flags;
        rflags |= nval;

        if ((options & osFlagsWaitAll) == osFlagsWaitAll) {
          if ((flags & rflags) == flags) {
            break;
          } else {
            if (timeout == 0U) {
              rflags = (uint32_t)osErrorResource;
              break;
            }
          }
        }
        else {
          if ((flags & rflags) != 0) {
            break;
          } else {
            if (timeout == 0U) {
              rflags = (uint32_t)osErrorResource;
              break;
            }
          }
        }

        /* Update timeout */
        td = xTaskGetTickCount() - t0;

        if (td > timeout) {
          tout  = 0;
        } else {
          tout = timeout - td;
        }
      }
      else {
        if (timeout == 0) {
          rflags = (uint32_t)osErrorResource;
        } else {
          rflags = (uint32_t)osErrorTimeout;
        }
      }
    }
    while (rval != pdFAIL);
  }

  /* Return flags before clearing */
  return (rflags);
}

uint32_t osEventFlagsSet (osEventFlagsId_t ef_id, uint32_t flags) {
  EventGroupHandle_t hEventGroup = (EventGroupHandle_t)ef_id;
  uint32_t rflags;
  BaseType_t yield;

  if ((hEventGroup == NULL) || ((flags & EVENT_FLAGS_INVALID_BITS) != 0U)) {
    rflags = (uint32_t)osErrorParameter;
  }
  else if (IRQ_Context() != 0U) {
  #if (configUSE_OS2_EVENTFLAGS_FROM_ISR == 0)
    (void)yield;
    /* Enable timers and xTimerPendFunctionCall function to support osEventFlagsSet from ISR */
    rflags = (uint32_t)osErrorResource;
  #else
    yield = pdFALSE;

    if (xEventGroupSetBitsFromISR (hEventGroup, (EventBits_t)flags, &yield) == pdFAIL) {
      rflags = (uint32_t)osErrorResource;
    } else {
      /* Retrieve bits that are already set and add flags to be set in current call */
      rflags  = xEventGroupGetBitsFromISR (hEventGroup);
      rflags |= flags;
      portYIELD_FROM_ISR (yield);
    }
  #endif
  }
  else {
    rflags = xEventGroupSetBits (hEventGroup, (EventBits_t)flags);
  }

  /* Return event flags after setting */
  return (rflags);
}

osStatus_t osDelay (uint32_t ticks) {
  osStatus_t stat;

  if (IRQ_Context() != 0U) {
    stat = osErrorISR;
  }
  else {
    stat = osOK;

    if (ticks != 0U) {
      vTaskDelay(ticks);
    }
  }

  /* Return execution status */
  return (stat);
}
