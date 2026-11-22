/*************************************************************************************************/
/*!
 *  \file
 *
 *  \brief  R1-owned WSF heap for the source-built Cordio controller.
 *
 *  Copyright (c) 2009-2018 Arm Ltd. All Rights Reserved.
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

#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "pal_sys.h"
#include "wsf_heap.h"

/* The R1 controller profile needs 5,196 bytes for WSF buffer pools and
 * 5,768 bytes for the measured link-layer reservation. Keep at least 3 KiB
 * beyond those allocations for profile drift; the bootstrap checks both
 * actual allocation sizes before accepting the controller. The remaining
 * lower RAM is needed by the source DFU host while the application is absent. */
#define R1_CORDIO_WSF_HEAP_BYTES 14336u
_Static_assert(R1_CORDIO_WSF_HEAP_BYTES >= 5196u + 5768u + 3072u,
               "WSF heap must cover measured controller and pool allocations");
_Static_assert((R1_CORDIO_WSF_HEAP_BYTES % 4u) == 0u, "WSF word alignment");

#if defined(__arm__)
__attribute__((section(".bss.r1_cordio_heap"), aligned(8)))
#else
__attribute__((aligned(8)))
#endif
static uint32_t r1CordioWsfHeap[R1_CORDIO_WSF_HEAP_BYTES / 4u];

uint8_t *SystemHeapStart;
uint32_t SystemHeapSize;
static bool r1CordioHeapInitialized;

void r1_cordio_wsf_heap_init(void)
{
  if (!r1CordioHeapInitialized)
  {
    memset(r1CordioWsfHeap, 0, sizeof(r1CordioWsfHeap));
    SystemHeapStart = (uint8_t *)r1CordioWsfHeap;
    SystemHeapSize = sizeof(r1CordioWsfHeap);
    r1CordioHeapInitialized = true;
  }
}

/* Keep the checked reservation separate from WSF's void API so callers and
 * host tests can distinguish exhaustion from a successful reservation. */
bool r1_cordio_wsf_heap_reserve(uint32_t size)
{
  if (!r1CordioHeapInitialized || size > UINT32_MAX - 3u)
  {
    return false;
  }
  uint32_t rounded = (size + 3u) & ~UINT32_C(3);
  if (rounded > SystemHeapSize)
  {
    return false;
  }
  SystemHeapStart += rounded;
  SystemHeapSize -= rounded;
  return true;
}

void WsfHeapAlloc(uint32_t size)
{
  if (!r1_cordio_wsf_heap_reserve(size))
  {
    PalSysAssertTrap();
    for (;;) { }
  }
}

void *WsfHeapGetFreeStartAddress(void)
{
  return SystemHeapStart;
}

uint32_t WsfHeapCountAvailable(void)
{
  return SystemHeapSize;
}

uint32_t WsfHeapCountUsed(void)
{
  return r1CordioHeapInitialized ? R1_CORDIO_WSF_HEAP_BYTES - SystemHeapSize : 0u;
}
#endif /* R1_CORDIO_RTC0 */
