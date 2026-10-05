/*************************************************************************************************/
/*!
 *  \file   wsf_timer.c
 *
 *  \brief  Timer service.
 *
 *  Copyright (c) 2009-2019 Arm Ltd. All Rights Reserved.
 *
 *  Copyright (c) 2019-2020 Packetcraft, Inc.
 *  
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  
 *      http://www.apache.org/licenses/LICENSE-2.0
 *  
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
/*************************************************************************************************/

#include "wsf_timer_compat.h"

void WsfQueueRemove(wsfQueue_t *pQueue, void *pElem, void *pPrev)
{
  WSF_CS_INIT(cs);

  WSF_ASSERT(pQueue != NULL);
  WSF_ASSERT(pQueue->pHead != NULL);
  WSF_ASSERT(pElem != NULL);

  /* enter critical section */
  WSF_CS_ENTER(cs);

  /* if first element */
  if (pElem == pQueue->pHead)
  {
    /* remove from head of queue */
    pQueue->pHead = WSF_QUEUE_NEXT(pElem);
  }
  else if (pPrev)
  {
    /* remove from middle of queue, pPrev will never be null */
    WSF_QUEUE_NEXT(pPrev) = WSF_QUEUE_NEXT(pElem);
  }

  /* if last element */
  if (pElem == pQueue->pTail)
  {
    /* update tail */
    pQueue->pTail = pPrev;
  }

  /* exit critical section */
  WSF_CS_EXIT(cs);
}

static void wsfTimerRemove(wsfTimer_t *pTimer)
{
  wsfTimer_t  *pElem;
  wsfTimer_t  *pPrev = NULL;

  pElem = (wsfTimer_t *) wsfTimerTimerQueue.pHead;

  /* find timer in queue */
  while (pElem != NULL)
  {
    if (pElem == pTimer)
    {
      break;
    }
    pPrev = pElem;
    pElem = pElem->pNext;
  }

  /* if timer found remove from queue */
  if (pElem != NULL)
  {
    WsfQueueRemove(&wsfTimerTimerQueue, pTimer, pPrev);

    pTimer->isStarted = FALSE;
  }
}

void WsfTimerStop(wsfTimer_t *pTimer)
{
  WSF_TRACE_INFO1("WsfTimerStop pTimer:0x%x", pTimer);

  /* task schedule lock */
  WsfTaskLock();

  wsfTimerRemove(pTimer);

  /* task schedule unlock */
  WsfTaskUnlock();
}

/* Original task-lock wrappers delegate to the existing reconstructed stock port.
 * That byte-depth port does not save/restore an unrelated incoming PRIMASK.
 */
void WsfTaskLock(void) { opencfw_wsf_cs_enter(); }
void WsfTaskUnlock(void) { opencfw_wsf_cs_exit(); }
void opencfw_wsf_timer_remove_raw(wsfTimer_t *timer) { wsfTimerRemove(timer); }
void opencfw_radio_timer_gpio_shutdown_phase(void)
{
    WsfTimerStop((wsfTimer_t *)(uintptr_t)0x20073e64u);
    opencfw_radio_gpio_shutdown_phase();
}
