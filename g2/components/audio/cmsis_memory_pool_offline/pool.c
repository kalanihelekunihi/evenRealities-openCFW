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
/* Stock-layout offline CMSIS provider. Public selected bodies below. */
#include "compat.h"
static void *CreateBlock (MemPool_t *mp) {
  MemPoolBlock_t *p = NULL;

  if (mp->n < mp->bl_cnt) {
    /* Unallocated blocks exist, set pointer to new block */
    p = (void *)(mp->mem_arr + (mp->bl_sz * mp->n));

    /* Increment block index */
    mp->n += 1U;
  }

  return (p);
}
static void *AllocBlock (MemPool_t *mp) {
  MemPoolBlock_t *p = NULL;

  if (mp->head != NULL) {
    /* List of free block exists, get head block */
    p = mp->head;

    /* Head block is now next on the list */
    mp->head = p->next;
  }

  return (p);
}
static void FreeBlock (MemPool_t *mp, void *block) {
  MemPoolBlock_t *p = block;

  /* Store current head into block memory space */
  p->next = mp->head;

  /* Store current block as new head */
  mp->head = p;
}
void *osMemoryPoolAlloc (osMemoryPoolId_t mp_id, uint32_t timeout) {
  MemPool_t *mp;
  void *block;
  uint32_t isrm;

  if (mp_id == NULL) {
    /* Invalid input parameters */
    block = NULL;
  }
  else {
    block = NULL;

    mp = (MemPool_t *)mp_id;

    if ((mp->status & MPOOL_STATUS) == MPOOL_STATUS) {
      if (IRQ_Context() != 0U) {
        if (timeout == 0U) {
          if (xSemaphoreTakeFromISR (mp->sem, NULL) == pdTRUE) {
            if ((mp->status & MPOOL_STATUS) == MPOOL_STATUS) {
              isrm  = taskENTER_CRITICAL_FROM_ISR();

              /* Get a block from the free-list */
              block = AllocBlock(mp);

              if (block == NULL) {
                /* List of free blocks is empty, 'create' new block */
                block = CreateBlock(mp);
              }

              taskEXIT_CRITICAL_FROM_ISR(isrm);
            }
          }
        }
      }
      else {
        if (xSemaphoreTake (mp->sem, (TickType_t)timeout) == pdTRUE) {
          if ((mp->status & MPOOL_STATUS) == MPOOL_STATUS) {
            taskENTER_CRITICAL();

            /* Get a block from the free-list */
            block = AllocBlock(mp);

            if (block == NULL) {
              /* List of free blocks is empty, 'create' new block */
              block = CreateBlock(mp);
            }

            taskEXIT_CRITICAL();
          }
        }
      }
    }
  }

  /* Return memory block address */
  return (block);
}
osStatus_t osMemoryPoolFree (osMemoryPoolId_t mp_id, void *block) {
  MemPool_t *mp;
  osStatus_t stat;
  uint32_t isrm;
  BaseType_t yield;

  if ((mp_id == NULL) || (block == NULL)) {
    /* Invalid input parameters */
    stat = osErrorParameter;
  }
  else {
    mp = (MemPool_t *)mp_id;

    if ((mp->status & MPOOL_STATUS) != MPOOL_STATUS) {
      /* Invalid object status */
      stat = osErrorResource;
    }
    else if ((block < (void *)&mp->mem_arr[0]) || (block > (void*)&mp->mem_arr[mp->mem_sz-1])) {
      /* Block pointer outside of memory array area */
      stat = osErrorParameter;
    }
    else {
      stat = osOK;

      if (IRQ_Context() != 0U) {
        if (uxSemaphoreGetCountFromISR (mp->sem) == mp->bl_cnt) {
          stat = osErrorResource;
        }
        else {
          isrm = taskENTER_CRITICAL_FROM_ISR();

          /* Add block to the list of free blocks */
          FreeBlock(mp, block);

          taskEXIT_CRITICAL_FROM_ISR(isrm);

          yield = pdFALSE;
          xSemaphoreGiveFromISR (mp->sem, &yield);
          portYIELD_FROM_ISR (yield);
        }
      }
      else {
        if (uxSemaphoreGetCount (mp->sem) == mp->bl_cnt) {
          stat = osErrorResource;
        }
        else {
          taskENTER_CRITICAL();

          /* Add block to the list of free blocks */
          FreeBlock(mp, block);

          taskEXIT_CRITICAL();

          xSemaphoreGive (mp->sem);
        }
      }
    }
  }

  /* Return execution status */
  return (stat);
}

osMemoryPoolId_t osMemoryPoolNew (uint32_t block_count, uint32_t block_size, const osMemoryPoolAttr_t *attr) {
  MemPool_t *mp;
  const char *name;
  int32_t mem_cb, mem_mp;
  uint32_t sz;

  if (IRQ_Context() != 0U) {
    mp = NULL;
  }
  else if ((block_count == 0U) || (block_size == 0U)) {
    mp = NULL;
  }
  else {
    mp = NULL;
    sz = MEMPOOL_ARR_SIZE (block_count, block_size);

    name = NULL;
    mem_cb = -1;
    mem_mp = -1;

    if (attr != NULL) {
      if (attr->name != NULL) {
        name = attr->name;
      }

      if ((attr->cb_mem != NULL) && (attr->cb_size >= sizeof(MemPool_t))) {
        /* Static control block is provided */
        mem_cb = 1;
      }
      else if ((attr->cb_mem == NULL) && (attr->cb_size == 0U)) {
        /* Allocate control block memory on heap */
        mem_cb = 0;
      }

      if ((attr->mp_mem == NULL) && (attr->mp_size == 0U)) {
        /* Allocate memory array on heap */
          mem_mp = 0;
      }
      else {
        if (attr->mp_mem != NULL) {
          /* Check if array is 4-byte aligned */
          if (((uint32_t)attr->mp_mem & 3U) == 0U) {
            /* Check if array big enough */
            if (attr->mp_size >= sz) {
              /* Static memory pool array is provided */
              mem_mp = 1;
            }
          }
        }
      }
    }
    else {
      /* Attributes not provided, allocate memory on heap */
      mem_cb = 0;
      mem_mp = 0;
    }

    if (mem_cb == 0) {
      mp = pvPortMalloc (sizeof(MemPool_t));
    } else {
      mp = attr->cb_mem;
    }

    if (mp != NULL) {
      /* Create a semaphore (max count == initial count == block_count) */
      #if (configSUPPORT_STATIC_ALLOCATION == 1)
        mp->sem = xSemaphoreCreateCountingStatic (block_count, block_count, &mp->mem_sem);
      #elif (configSUPPORT_DYNAMIC_ALLOCATION == 1)
        mp->sem = xSemaphoreCreateCounting (block_count, block_count);
      #else
        mp->sem = NULL;
      #endif

      if (mp->sem != NULL) {
        /* Setup memory array */
        if (mem_mp == 0) {
          mp->mem_arr = pvPortMalloc (sz);
        } else {
          mp->mem_arr = attr->mp_mem;
        }
      }
    }

    if ((mp != NULL) && (mp->mem_arr != NULL)) {
      /* Memory pool can be created */
      mp->head    = NULL;
      mp->mem_sz  = sz;
      mp->name    = name;
      mp->bl_sz   = block_size;
      mp->bl_cnt  = block_count;
      mp->n       = 0U;

      /* Set heap allocated memory flags */
      mp->status = MPOOL_STATUS;

      if (mem_cb == 0) {
        /* Control block on heap */
        mp->status |= 1U;
      }
      if (mem_mp == 0) {
        /* Memory array on heap */
        mp->status |= 2U;
      }
    }
    else {
      /* Memory pool cannot be created, release allocated resources */
      if ((mem_cb == 0) && (mp != NULL)) {
        /* Free control block memory */
        vPortFree (mp);
      }
      mp = NULL;
    }
  }

  /* Return memory pool ID */
  return (mp);
}
