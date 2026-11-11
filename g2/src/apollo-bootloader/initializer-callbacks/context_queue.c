/* SPDX-License-Identifier: MIT. Stock42c3e2,42c420,42c44e IOM CQ adapters. */
#include "context_claim.h"
#include <stdbool.h>
#include "am_hal_cmdq.h" /* AmbiqSuite 5.1.0; stock 0x427754..0x427c72 */
#define WORD(h,o) (*(volatile uint32_t *)((uintptr_t)(h)+(o)))
/* Stock 0x42c3e2 (cmdq_adapter_init_42c3e2) */
uint32_t opencfw_boot_iom_cq_initialize(void *handle,uint32_t words,uint32_t buffer)
{
    struct opencfw_iom_context *h=handle;
    am_hal_cmdq_cfg_t config;
    WORD(h,0x828u)=0u;WORD(h,0x20u)=0u;WORD(h,0x85cu)=0u;
    config.cmdQSize=words>>1;config.pCmdQBuf=(uint32_t *)(uintptr_t)buffer;config.priority=AM_HAL_CMDQ_PRIO_HI;
    uint32_t status=am_hal_cmdq_init((am_hal_cmdq_if_e)(uint8_t)h->module,&config,
                                         (void **)(uintptr_t)((uintptr_t)h+0x828u));
    if (!status) WORD(h,0x20u)=256u;
    return status;
}
/* Stock 0x42c420 (cmdq_adapter_enable_42c420) */
uint32_t opencfw_boot_iom_cq_enable(void *handle)
{
    struct opencfw_iom_context *h=handle;
    if (!WORD(h,0x24u)) {
        uintptr_t reg=0x4005022cu+h->module*0x1000u;
        uint32_t buffer=*(volatile uint32_t *)reg;
        *(volatile uint32_t *)(uintptr_t)buffer=(uint32_t)reg;
        *(volatile uint32_t *)(uintptr_t)(buffer+4u)=buffer;
    }
    return am_hal_cmdq_enable((void *)(uintptr_t)WORD(h,0x828u));
}
/* Stock 0x42c44e (cmdq_adapter_disable_42c44e) */
uint32_t opencfw_boot_iom_cq_disable(void *handle)
{
    return am_hal_cmdq_disable((void *)(uintptr_t)WORD(handle,0x828u));
}
