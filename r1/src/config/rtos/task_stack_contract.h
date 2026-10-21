#ifndef R1_TASK_STACK_CONTRACT_H
#define R1_TASK_STACK_CONTRACT_H
#include "FreeRTOS.h"
#define uxCriticalNesting (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007814))
#define portINITIAL_XPSR ((StackType_t)UINT32_C(0x01000000))
#define portINITIAL_EXEC_RETURN UINT32_C(0xfffffffd)
#define portTASK_RETURN_ADDRESS prvTaskExitError
static void prvTaskExitError(void);
#endif
