/* SPDX-License-Identifier: MIT */
/* Recovered model task setter. Exact linked stock bytes checked; hardware qualification pending. */
#include <stddef.h>
#include <stdint.h>
#include <driver/gx_snpu.h>

extern void *open_cfw_gx8002_memcpy(void *, const void *, size_t);
#ifndef OPEN_CFW_GX8002_MODEL_HOST_TEST
_Static_assert(sizeof(GX_SNPU_TASK) == 32, "GRUS task ABI");
#define TASK_DESTINATION ((void *)(uintptr_t)0x2002E85CU)
#else
extern GX_SNPU_TASK open_cfw_gx8002_saved_task;
#define TASK_DESTINATION ((void *)&open_cfw_gx8002_saved_task)
#endif

void LvpSetSnpuTask(GX_SNPU_TASK *task)
{
    (void)open_cfw_gx8002_memcpy(TASK_DESTINATION, task, sizeof(*task));
}
