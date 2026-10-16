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
#include "timer_new_contract.h"
typedef struct {
  osTimerFunc_t func;
  void         *arg;
} TimerCallback_t;
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

static void TimerCallback (TimerHandle_t hTimer) {
  TimerCallback_t *callb;

  /* Retrieve pointer to callback function and argument */
  callb = (TimerCallback_t *)pvTimerGetTimerID (hTimer);

  /* Remove dynamic allocation flag */
  callb = (TimerCallback_t *)((uint32_t)callb & ~1U);

  if (callb != NULL) {
    callb->func (callb->arg);
  }
}

osTimerId_t osTimerNew (osTimerFunc_t func, osTimerType_t type, void *argument, const osTimerAttr_t *attr) {
  const char *name;
  TimerHandle_t hTimer;
  TimerCallback_t *callb;
  UBaseType_t reload;
  int32_t mem;
  uint32_t callb_dyn;

  hTimer = NULL;

  if ((IRQ_Context() == 0U) && (func != NULL)) {
    callb     = NULL;
    callb_dyn = 0U;

    #if (configSUPPORT_STATIC_ALLOCATION == 1)
      /* Static memory allocation is available: check if memory for control block */
      /* is provided and if it also contains space for callback and its argument  */
      if ((attr != NULL) && (attr->cb_mem != NULL)) {
        if (attr->cb_size >= (sizeof(StaticTimer_t) + sizeof(TimerCallback_t))) {
          callb = (TimerCallback_t *)((uint32_t)attr->cb_mem + sizeof(StaticTimer_t));
        }
      }
    #endif

    #if (configSUPPORT_DYNAMIC_ALLOCATION == 1)
      /* Dynamic memory allocation is available: if memory for callback and */
      /* its argument is not provided, allocate it from dynamic memory pool */
      if (callb == NULL) {
        callb = (TimerCallback_t *)pvPortMalloc (sizeof(TimerCallback_t));

        if (callb != NULL) {
          /* Callback memory was allocated from dynamic pool, set flag */
          callb_dyn = 1U;
        }
      }
    #endif

    if (callb != NULL) {
      callb->func = func;
      callb->arg  = argument;

      if (type == osTimerOnce) {
        reload = pdFALSE;
      } else {
        reload = pdTRUE;
      }

      mem  = -1;
      name = NULL;

      if (attr != NULL) {
        if (attr->name != NULL) {
          name = attr->name;
        }

        if ((attr->cb_mem != NULL) && (attr->cb_size >= sizeof(StaticTimer_t))) {
          /* The memory for control block is provided, use static object */
          mem = 1;
        }
        else {
          if ((attr->cb_mem == NULL) && (attr->cb_size == 0U)) {
            /* Control block will be allocated from the dynamic pool */
            mem = 0;
          }
        }
      }
      else {
        mem = 0;
      }
      /* Store callback memory dynamic allocation flag */
      callb = (TimerCallback_t *)((uint32_t)callb | callb_dyn);
      /*
        TimerCallback function is always provided as a callback and is used to call application
        specified function with its argument both stored in structure callb.
      */
      if (mem == 1) {
        #if (configSUPPORT_STATIC_ALLOCATION == 1)
          hTimer = xTimerCreateStatic (name, 1, reload, callb, TimerCallback, (StaticTimer_t *)attr->cb_mem);
        #endif
      }
      else {
        if (mem == 0) {
          #if (configSUPPORT_DYNAMIC_ALLOCATION == 1)
            hTimer = xTimerCreate (name, 1, reload, callb, TimerCallback);
          #endif
        }
      }

      #if (configSUPPORT_DYNAMIC_ALLOCATION == 1)
      if ((hTimer == NULL) && (callb != NULL) && (callb_dyn == 1U)) {
        /* Failed to create a timer, release allocated resources */
        callb = (TimerCallback_t *)((uint32_t)callb & ~1U);

        vPortFree (callb);
      }
      #endif
    }
  }

  /* Return timer ID */
  return ((osTimerId_t)hTimer);
}
