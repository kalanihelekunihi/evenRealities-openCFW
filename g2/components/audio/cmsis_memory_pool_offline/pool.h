#ifndef OPENCFW_OFFLINE_CMSIS_POOL_H
#define OPENCFW_OFFLINE_CMSIS_POOL_H
#include <stdint.h>
#include "../queue_cmsis_offline/queue.h"
typedef struct MemPoolBlock {struct MemPoolBlock *next;} MemPoolBlock_t;
typedef struct {MemPoolBlock_t *head;QueueHandle_t sem;uint8_t *mem_arr;uint32_t mem_sz;const char *name;uint32_t bl_sz,bl_cnt,n,status;Queue_t mem_sem;} MemPool_t;
typedef struct {const char *name;uint32_t attr_bits;void *cb_mem;uint32_t cb_size;void *mp_mem;uint32_t mp_size;} osMemoryPoolAttr_t;
void *osMemoryPoolNew(uint32_t count,uint32_t size,const osMemoryPoolAttr_t *attr);
void *osMemoryPoolAlloc(void *pool,uint32_t timeout_ticks);
int32_t osMemoryPoolFree(void *pool,void *block);
#endif
