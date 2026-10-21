/* SPDX-License-Identifier: MIT
 * Native XIP SNPU lifecycle 0x10205cf4/0x10205d40.
 */
#include <stdint.h>

extern void gx8002_xip_snpu_device_initialize_102055a8(uint32_t);
extern void gx8002_xip_snpu_device_exit_102055ac(void);
extern void gx8002_xip_snpu_request_irq_102055b0(uint32_t, uint32_t);
extern void gx8002_xip_snpu_tcb_initialize_102058d4(void);
extern int32_t gx8002_xip_snpu_suspend_10205a90(void);
extern void gx8002_resident_mask_irq_254fc(uint32_t);
extern void gx8002_resident_unmask_irq_25504(uint32_t);

static volatile uint32_t *const snpu_state =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027350);

uint32_t gx8002_xip_snpu_initialize_10205cf4(void)
{
    gx8002_xip_snpu_device_initialize_102055a8(UINT32_C(0xa0c00000));
    snpu_state[0x5c4u / 4u] = UINT32_C(0xa0c00000);
    snpu_state[0x5c8u / 4u] = UINT32_C(0xa0300000);
    snpu_state[0x5ccu / 4u] = UINT32_C(0xa0c00190);
    snpu_state[0x5b4u / 4u] = 0u;
    snpu_state[0x5b0u / 4u] = 0u;
    gx8002_xip_snpu_tcb_initialize_102058d4();
    gx8002_xip_snpu_request_irq_102055b0(UINT32_C(0x10205ce0), 0u);
    snpu_state[0] = 2u;
    return 0u;
}

int32_t gx8002_xip_snpu_exit_10205d40(void)
{
    gx8002_resident_mask_irq_254fc(12u);
    int32_t result = gx8002_xip_snpu_suspend_10205a90();
    gx8002_resident_unmask_irq_25504(12u);
    if (result == 0) gx8002_xip_snpu_device_exit_102055ac();
    return result;
}
