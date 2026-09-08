/* SPDX-License-Identifier: MIT */
/* Reconstructed from GX8002 stock control flow, cross-identified using
 * authenticated NationalChip driver object symbols and relocations.
 * Driver objects are comparison oracles only; no object bytes are included. */
#include <driver-exit-interfaces.h>
extern int open_cfw_gx8002_snpu_suspend(void);
extern void open_cfw_gx8002_snpu_device_exit(void);
extern int open_cfw_gx8002_audio_reset(void);
extern void open_cfw_gx8002_platform_gate(unsigned int, unsigned int);
int gx_snpu_exit(void)
{
    gx_mask_irq(12);
    int result = open_cfw_gx8002_snpu_suspend();
    gx_unmask_irq(12);
    if (result == 0)
        open_cfw_gx8002_snpu_device_exit();
    return result;
}
int gx_audio_in_exit(void)
{
    open_cfw_gx8002_audio_reset();
    open_cfw_gx8002_platform_gate(3, 0);
    open_cfw_gx8002_platform_gate(2, 0);
    open_cfw_gx8002_platform_gate(8, 0);
    open_cfw_gx8002_platform_gate(7, 0);
    return 0;
}
