#ifndef R1_UNORDERED_EVENT_CONTRACT_H
#define R1_UNORDERED_EVENT_CONTRACT_H
#include "mutex_tasks_contract.h"
#define uxSchedulerSuspended (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007850))
static void prvResetNextTaskUnblockTime(void);
#endif
