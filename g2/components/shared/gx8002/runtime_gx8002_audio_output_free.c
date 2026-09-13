/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
extern void *memset(void *,int,size_t);
/* Stock e86c omits _aout_reset present in pinned upstream aout_free.
 * Preserve read-before-zero accesses and the late handle guard. */
int open_cfw_gx8002_aout_free(void *handle)
{
    volatile uint32_t *irq=(volatile uint32_t *)0xa0b00008u;
    *irq=*irq&~1u;
    volatile uint32_t *sdc=(volatile uint32_t *)0xa0b80000u;
    (void)sdc[5];sdc[5]=0;
    (void)sdc[6];sdc[6]=0;
    memset((void *)((uintptr_t)handle+16),0,36);
    if (handle) {
        volatile uint8_t *active=(volatile uint8_t *)handle+4;
        if (*(const uint8_t *)active) *active=0;
    }
    return 0;
}
