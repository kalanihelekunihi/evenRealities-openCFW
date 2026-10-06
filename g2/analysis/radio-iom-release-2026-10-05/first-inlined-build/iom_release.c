/* SPDX-License-Identifier: MIT */
/* Reconstructed stock IOM consumer chain; no SDK source attribution for these
 * bodies. CMDQ provider is unchanged pinned Ambiq code with retained notices. */
#include "iom_release.h"
#include "../ambiq_mspi/ambiq_cmdq.h"
static volatile uint32_t *field(void *handle,uint32_t offset)
{ return (volatile uint32_t *)((uint8_t *)handle+offset); }
static bool valid(void *handle)
{ return handle && ((*field(handle,0)&0x01ffffffu)==0x01123456u); }
uint32_t opencfw_iom_cq_term(void *handle)
{
    if(*field(handle,0x828)) {
        (void)am_hal_cmdq_term((void *)(uintptr_t)*field(handle,0x828),true);
        *field(handle,0x828)=0;
    }
    return 0;
}
uint32_t opencfw_iom_disable(void *handle)
{
    if(!valid(handle))return 2;
    if(!(*field(handle,0)&0x02000000u))return 0;
    if(*field(handle,0x24))return 3;
    volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)
        (0x40050000u+(*field(handle,4)<<12)+0x11cu);
    *reg &= ~1u;
    reg=(volatile uint32_t *)(uintptr_t)
        (0x40050000u+(*field(handle,4)<<12)+0x11cu);
    *reg &= ~0x10u;
    (void)opencfw_iom_cq_term(handle);
    *field(handle,0) &= ~0x02000000u;
    return 0;
}
uint32_t opencfw_iom_uninitialize(void *handle)
{
    if(!valid(handle))return 2;
    if(*field(handle,0)&0x02000000u)(void)opencfw_iom_disable(handle);
    *field(handle,0) &= ~0x01000000u;
    return 0;
}
