/*************************************************************************************************/
/*!
 *  \file
 *
 *  \brief  System hooks.
 *
 *  Copyright (c) 2013-2019 Arm Ltd. All Rights Reserved.
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

/* R1 port: share the recovered Nordic clock manager and preserve PRIMASK
 * across Cordio critical sections. The pinned PAL remains unmodified. */
#if defined(R1_CORDIO_RTC0)
#include "nrf.h"
#include "nrf_drv_clock.h"
#include "pal_rtc.h"
#include "pal_sys.h"
#include "pal_timer.h"
#include "pal_bb.h"
#include "pal_uart.h"

#include <stdbool.h>
#include <string.h>

/**************************************************************************************************
  Macros
**************************************************************************************************/

/*! \brief      Stack initial values. */
#define INIT_STACK_VAL      0xAFAFAFAF
extern uint32_t __StackLimit;
extern uint32_t __StackTop;
extern void r1_cordio_wsf_heap_init(void);
extern uint8_t *SystemHeapStart;
extern uint32_t SystemHeapSize;

/**************************************************************************************************
  Global Variables
**************************************************************************************************/

/*! \brief      Number of assertions. */
static uint32_t palSysAssertCount;

/*! \brief      Trap enabled flag. */
static volatile bool_t PalSysAssertTrapEnable;

static uint32_t palSysBusyCount;
static bool palSysHfclkRequested;
static uint32_t palCsDepth;
static uint32_t palCsSavedPrimask;

void r1_cordio_sys_release_hfclk(void)
{
  if (palSysHfclkRequested)
  {
    nrf_drv_clock_hfclk_release();
    palSysHfclkRequested = false;
  }
}

/**************************************************************************************************
  Functions
**************************************************************************************************/

/*************************************************************************************************/
/*!
 *  \brief  Enter a critical section.
 */
/*************************************************************************************************/
void PalEnterCs(void)
{
  uint32_t prior = __get_PRIMASK();
  __disable_irq();
  if (palCsDepth == 0)
  {
    palCsSavedPrimask = prior;
  }
  palCsDepth++;
}

/*************************************************************************************************/
/*!
 *  \brief  Exit a critical section.
 */
/*************************************************************************************************/
void PalExitCs(void)
{
  uint32_t prior = __get_PRIMASK();
  __disable_irq();
  if (palCsDepth == 0)
  {
    __set_PRIMASK(prior);
    return;
  }
  if (--palCsDepth == 0)
  {
    __set_PRIMASK(palCsSavedPrimask);
  }
}

/*************************************************************************************************/
/*!
 *  \brief      Common platform initialization.
 */
/*************************************************************************************************/
void PalSysInit(void)
{
  /* Enable Flash cache */
  NRF_NVMC->ICACHECNF |= (NVMC_ICACHECNF_CACHEEN_Enabled << NVMC_ICACHECNF_CACHEEN_Pos);

  /* R1 initializes nrf_drv_clock before this bootstrap. Hold one crystal
   * reference for Cordio instead of bypassing the shared HFCLK manager. */
  if (!palSysHfclkRequested)
  {
    nrf_drv_clock_hfclk_request(NULL);
    palSysHfclkRequested = true;
  }
  while (!nrf_drv_clock_hfclk_is_running()) { }

  palSysAssertCount = 0;
  PalSysAssertTrapEnable = TRUE;
  palSysBusyCount = 0;

  r1_cordio_wsf_heap_init();
  PalRtcInit();

#ifdef DEBUG
  /* Reset free memory. */
  memset(SystemHeapStart, 0, SystemHeapSize);
#endif
}

/*************************************************************************************************/
/*!
 *  \brief      System fault trap.
 */
/*************************************************************************************************/
void PalSysAssertTrap(void)
{
  palSysAssertCount++;

  while (PalSysAssertTrapEnable);
}

/*************************************************************************************************/
/*!
 *  \brief      Set system trap.
 *
 *  \param      enable    Enable assert trap or not.
 */
/*************************************************************************************************/
void PalSysSetTrap(bool_t enable)
{
  PalSysAssertTrapEnable = enable;
}

/*************************************************************************************************/
/*!
 *  \brief      Get assert count.
 */
/*************************************************************************************************/
uint32_t PalSysGetAssertCount(void)
{
  return palSysAssertCount;
}

/*************************************************************************************************/
/*!
 *  \brief      Count stack usage.
 *
 *  \return     Number of bytes used by the stack.
 */
/*************************************************************************************************/
uint32_t PalSysGetStackUsage(void)
{
  uintptr_t pUnused = (uintptr_t)&__StackLimit;
  uintptr_t top = (uintptr_t)&__StackTop;

  while (pUnused < top)
  {
    if (*(const uint32_t *)pUnused != INIT_STACK_VAL)
    {
      break;
    }

    pUnused += sizeof(uint32_t);
  }

  return (uint32_t)(top - pUnused);
}

/*************************************************************************************************/
/*!
 *  \brief      System sleep.
 */
/*************************************************************************************************/
void PalSysSleep(void)
{
  /* The R1 clock manager owns Cordio's HFCLK reference during sleep. */

  __WFI();
}

/*************************************************************************************************/
/*!
 *  \brief      Check if system is busy.
 *
 *  \return     TRUE if system is busy.
 */
/*************************************************************************************************/
bool_t PalSysIsBusy(void)
{
  bool_t sysIsBusy = FALSE;
  PalEnterCs();
  sysIsBusy = ((palSysBusyCount == 0) ? FALSE : TRUE);
  PalExitCs();
  return sysIsBusy;
}

/*************************************************************************************************/
/*!
 *  \brief      Set system busy.
 *
 *  \return     none.
 */
/*************************************************************************************************/
void PalSysSetBusy(void)
{
  PalEnterCs();
  palSysBusyCount++;
  PalExitCs();
}

/*************************************************************************************************/
/*!
 *  \brief      Set system idle.
 */
/*************************************************************************************************/
void PalSysSetIdle(void)
{
  PalEnterCs();
  if (palSysBusyCount)
  {
    palSysBusyCount--;
  }
  PalExitCs();
}
#endif /* R1_CORDIO_RTC0 */
