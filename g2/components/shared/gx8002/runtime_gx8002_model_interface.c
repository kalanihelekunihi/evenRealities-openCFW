/* SPDX-License-Identifier: MIT */
/* Recovered model interface; task layout comes from pinned upstream GRUS SDK.
 * Sizes and offsets are runtime ABI facts, not a claim to recover the graph,
 * model weights, tensor interpretation, or NPU command semantics.
 */
#include <stdint.h>
#include <driver/gx_snpu.h>

#ifndef OPEN_CFW_GX8002_MODEL_HOST_TEST
_Static_assert(sizeof(GX_SNPU_TASK) == 32, "GRUS task ABI");
#define SAVED_TASK ((const volatile GX_SNPU_TASK *)(uintptr_t)0x2002E85CU)
#else
extern GX_SNPU_TASK open_cfw_gx8002_saved_task;
#define SAVED_TASK ((const volatile GX_SNPU_TASK *)&open_cfw_gx8002_saved_task)
#endif

static inline void *device_pointer(const void *pointer)
{
    return (void *)((uintptr_t)pointer & 0x0FFFFFFFU);
}

int LvpModelGetCmdSize(void) { return 9164; }
int LvpModelGetWeightSize(void) { return 120800; }
int LvpModelGetOpsSize(void) { return 0; }
int LvpModelGetDataSize(void) { return 13056; }
int LvpModelGetTmpSize(void) { return 4; }

int LvpCTCModelInitSnpuTask(GX_SNPU_TASK *task)
{
    task->module_id = 0x100;
    task->cmd = device_pointer(SAVED_TASK->cmd);
    task->weight = device_pointer(SAVED_TASK->weight);
    task->ops = device_pointer(SAVED_TASK->ops);
    void *data = device_pointer(SAVED_TASK->data);
    void *temporary = device_pointer(SAVED_TASK->tmp_mem);
    task->data = data;
    task->tmp_mem = temporary;
    return 0;
}

void *LvpCTCModelGetSnpuOutBuffer(void *buffer)
{
    return (void *)((uintptr_t)buffer + 8464U);
}

void *LvpCTCModelGetSnpuFeatsBuffer(void *buffer)
{
    return buffer;
}

void *LvpCTCModelGetSnpuStateBuffer(void *buffer)
{
    return (void *)((uintptr_t)buffer + 1040U);
}

unsigned int LvpCTCModelGetSnpuFeatsDim(void) { return 520; }
