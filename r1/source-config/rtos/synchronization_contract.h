#ifndef R1_SYNCHRONIZATION_CONTRACT_H
#define R1_SYNCHRONIZATION_CONTRACT_H
#include "message_queue_contract.h"
#include "semphr.h"
_Static_assert(sizeof(StaticSemaphore_t)==80 && sizeof(osMutexAttr_t)==16 && offsetof(osMutexAttr_t,cb_mem)==8,"native CMSIS mutex layout");
_Static_assert(configUSE_MUTEXES==1 && configUSE_RECURSIVE_MUTEXES==1,"native mutex variant");
#endif
