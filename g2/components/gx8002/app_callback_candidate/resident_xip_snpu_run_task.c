/* SPDX-License-Identifier: MIT
 * Native XIP 0x10205d60..0x10205e1d. The 0x20027350 control base
 * and 0x004100ff command word are authenticated literal-pool values.
 * Task's eight words match pinned NationalChip GX_SNPU_TASK layout.
 * Resume/submit descendants remain genuine separate source contracts.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_snpu_resume_internal_1020599c(void);
extern void gx8002_xip_snpu_submit_task_10205a00(uint32_t *);

int32_t gx8002_xip_tws_submit_10205d60(
    const uint32_t *task,
    uint32_t (*callback)(uint32_t, uint32_t, uint32_t), void *userdata)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027350);
    if (task == 0 || control[0x171u] == 0u ||
        ((int32_t)(control[0x16du] + 1u) % 10) ==
            (int32_t)control[0x16cu])
        return -1;
    uint32_t index = control[0x16du];
    volatile uint32_t *node = control + index * 0x24u + 4u;
    node[0x20u] = (uint32_t)(uintptr_t)callback;
    node[0x22u] = (uint32_t)(uintptr_t)userdata;
    node[6u] = task[1u];
    node[9u] = task[2u];
    node[0x21u] = task[0u];
    node[12u] = task[5u];
    node[15u] = task[3u];
    node[18u] = task[4u];
    node[21u] = task[6u];
    node[24u] = task[7u];
    uint32_t command_addr = (uint32_t)(uintptr_t)node & 0x0fffffffu;
    node[27u] = command_addr;
    node[30u] = UINT32_C(0xfffffffe);
    node[0u] = UINT32_C(0x004100ff);
    node[1u] = command_addr;
    node[29u] = task[5u];
    control[0x16du] = (uint32_t)((int32_t)(control[0x16du] + 1u) % 10);
    if (control[0] == 2u)
        (void)gx8002_xip_snpu_resume_internal_1020599c();
    gx8002_xip_snpu_submit_task_10205a00((uint32_t *)(uintptr_t)node);
    return 0;
}
