#ifndef R1_NATIVE_TASK_CONSTRUCTION_H
#define R1_NATIVE_TASK_CONSTRUCTION_H
#include <stdint.h>
#include <stddef.h>
#include "FreeRTOS.h"
#include "list.h"
typedef struct tskTaskControlBlock {
 uint32_t *pxTopOfStack;ListItem_t xStateListItem,xEventListItem;
 uint32_t uxPriority;uint32_t *pxStack;char pcTaskName[32];
 uint32_t uxNativeStackDepth,uxTCBNumber,opaque92,uxBasePriority,uxMutexesHeld;
 volatile uint32_t ulNotifiedValue;volatile uint8_t ucNotifyState;
 uint8_t ucStaticallyAllocated,padding110[2];
} r1_native_tcb;
_Static_assert(sizeof(r1_native_tcb)==112 && offsetof(r1_native_tcb,uxNativeStackDepth)==84 && offsetof(r1_native_tcb,uxTCBNumber)==88 && offsetof(r1_native_tcb,uxBasePriority)==96 && offsetof(r1_native_tcb,uxMutexesHeld)==100 && offsetof(r1_native_tcb,ulNotifiedValue)==104 && offsetof(r1_native_tcb,ucNotifyState)==108 && offsetof(r1_native_tcb,ucStaticallyAllocated)==109,"native task construction ABI");
void r1_native_task_initialize(TaskFunction_t,const char *,uint32_t,void *,uint32_t,r1_native_tcb **,r1_native_tcb *,const void *);
void r1_native_task_add_ready(r1_native_tcb *);
int32_t r1_native_task_create(TaskFunction_t,const char *,uint32_t,void *,uint32_t,r1_native_tcb **);
r1_native_tcb *r1_native_task_create_static(TaskFunction_t,const char *,uint32_t,void *,uint32_t,uint32_t *,r1_native_tcb *);
#endif
