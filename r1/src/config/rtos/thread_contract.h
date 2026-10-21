#ifndef R1_THREAD_CONTRACT_H
#define R1_THREAD_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "cmsis_os2.h"
#include "../../application/board/native_task_construction.h"
/* Scoped wrapper ABI. Baseline StaticTask_t and kernel configuration stay intact. */
#define StaticTask_t r1_native_tcb
#define xTaskCreate r1_native_task_create
#define xTaskCreateStatic r1_native_task_create_static
_Static_assert(sizeof(StaticTask_t)==112 && sizeof(osPriority_t)==4 && sizeof(StackType_t)==4,"native CMSIS task representation");
_Static_assert(offsetof(osThreadAttr_t,cb_mem)==8 && offsetof(osThreadAttr_t,cb_size)==12 && offsetof(osThreadAttr_t,stack_mem)==16 && offsetof(osThreadAttr_t,stack_size)==20 && offsetof(osThreadAttr_t,priority)==24 && sizeof(osThreadAttr_t)==36,"native thread attributes");
_Static_assert(configMINIMAL_STACK_SIZE==256 && osPriorityNormal==24 && osPriorityISR==56 && sizeof(configSTACK_DEPTH_TYPE)==2,"native wrapper defaults and dynamic depth narrowing");
#endif
