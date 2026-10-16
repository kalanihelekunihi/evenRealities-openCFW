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
#include "thread_contract.h"
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

osStatus_t osThreadTerminate (osThreadId_t thread_id) {
  TaskHandle_t hTask = (TaskHandle_t)thread_id;
  osStatus_t stat;
#ifndef USE_FreeRTOS_HEAP_1
  eTaskState tstate;

  if (IRQ_Context() != 0U) {
    stat = osErrorISR;
  }
  else if (hTask == NULL) {
    stat = osErrorParameter;
  }
  else {
    tstate = eTaskGetState (hTask);

    if (tstate != eDeleted) {
      stat = osOK;
      vTaskDelete (hTask);
    } else {
      stat = osErrorResource;
    }
  }
#else
  stat = osError;
#endif

  /* Return execution status */
  return (stat);
}
