#ifndef R1_TASK_STACK_CONTRACT_H
#define R1_TASK_STACK_CONTRACT_H
#include "FreeRTOS.h"
#define uxCriticalNesting (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007814))
/* Stock 0x856c2/0x856c6 loads the source-owned firmware word. */
extern const uint32_t r1_native_initial_xpsr;
#define portINITIAL_XPSR (*(const volatile StackType_t *)&r1_native_initial_xpsr)
#define portINITIAL_EXEC_RETURN UINT32_C(0xfffffffd)
#define portTASK_RETURN_ADDRESS prvTaskExitError
static void prvTaskExitError(void);
#endif
