/* SPDX-License-Identifier: MIT. Stock42c3e2,42c420,42c44e IOM CQ adapters. */
#include "context_claim.h"
#include "../nor_mspi_queue/nor_mspi_queue.h"
#define WORD(h,o) (*(volatile uint32_t *)((uintptr_t)(h)+(o)))
uint32_t opencfw_boot_iom_cq_initialize(void *handle,uint32_t words,uint32_t buffer)
{
    struct opencfw_iom_context *h=handle;
    struct {uint32_t half_units,buffer;uint8_t option,pad[3];} config;
    WORD(h,0x828u)=0u;WORD(h,0x20u)=0u;WORD(h,0x85cu)=0u;
    config.half_units=words>>1;config.buffer=buffer;config.option=1u;
    uint32_t status=opencfw_provider_427794((uint8_t)h->module,&config,
                                         (void **)(uintptr_t)((uintptr_t)h+0x828u));
    if (!status) WORD(h,0x20u)=256u;
    return status;
}
uint32_t opencfw_boot_iom_cq_enable(void *handle)
{
    struct opencfw_iom_context *h=handle;
    if (!WORD(h,0x24u)) {
        uintptr_t reg=0x4005022cu+h->module*0x1000u;
        uint32_t buffer=*(volatile uint32_t *)reg;
        *(volatile uint32_t *)(uintptr_t)buffer=(uint32_t)reg;
        *(volatile uint32_t *)(uintptr_t)(buffer+4u)=buffer;
    }
    return opencfw_provider_427878((uint32_t *)(uintptr_t)WORD(h,0x828u));
}
uint32_t opencfw_boot_iom_cq_disable(void *handle)
{
    return opencfw_provider_4278c8((uint32_t *)(uintptr_t)WORD(handle,0x828u));
}
