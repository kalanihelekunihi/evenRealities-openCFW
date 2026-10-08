/* SPDX-License-Identifier: MIT
 * Request 30 and its completion callback from stock HAL control 0x4251c0.
 * Queue/MMIO state is real target state; tests use explicit synthetic memory.
 */
#include "control_request_helpers.h"
#include "control_request_transactions.h"
#include <stddef.h>
#include <stdint.h>

#define MSPI_BASE UINT32_C(0x40060000)

extern uint32_t opencfw_provider_42790a(uint32_t *queue,
    uint32_t block_count,uint32_t *block_out,uint32_t *sequence_out);
extern uint32_t opencfw_provider_4279f0(uint32_t *queue,uint32_t kind);
extern uint32_t opencfw_provider_427878(uint32_t *queue);
extern uint32_t opencfw_provider_4279be(uint32_t queue);
extern uint32_t opencfw_provider_427c12(uint32_t queue,uint32_t kind);
extern uint32_t opencfw_bl_critical_save(void);
extern uint32_t clock_request(uint32_t clock_id,uint32_t user_id);

static uint32_t enable_queue(uint32_t *handle)
{
    const uint32_t user=(handle[1]+0x10u)&0xffu;
    const uint32_t status=clock_request(4u,user);
    if(status!=0u)return status;
    (void)opencfw_provider_427878((uint32_t *)(uintptr_t)handle[0x20a]);
    return 0u;
}

static uint32_t request30(uint32_t *handle,const uint8_t *config)
{
    const uint32_t module=handle[1];
    uint32_t *const queue=(uint32_t *)(uintptr_t)handle[0x20a];
    uint32_t block,sequence,status;
    uint32_t saved_mask;
    const uint32_t first_stage=config!=NULL && config[0]!=0u &&
        *(volatile uint8_t *)((uintptr_t)handle+0x82du)==0u;

    if(config==NULL)return 6u;
    if((config[4]&0xe0u)!=0u ||
       (*(const volatile uint32_t *)(const void *)(config+8)&0x00e0e0e0u)!=0u)
        return 6u;
    if(*(volatile uint8_t *)((uintptr_t)handle+0x82cu)!=1u)return 7u;

    if(handle[0x20e]!=0u){
        handle[0x20e]=0u;
        if(*(volatile uint8_t *)((uintptr_t)handle+0x8c8u)==0u)
            __asm__ volatile("dmb sy" ::: "memory");
        *(volatile uint32_t *)(uintptr_t)(MSPI_BASE+(module<<12)+0x2b4u)=0x20u;
    }

    if(first_stage){
        status=opencfw_provider_42790a(queue,1u,&block,&sequence);
        if(status!=0u)return status;
        const uint32_t slot=sequence&0xffu;
        handle[(0x28u>>2)+slot]=(uint32_t)(uintptr_t)&opencfw_bl_control_request_completion;
        handle[(0x428u>>2)+slot]=(uint32_t)(uintptr_t)handle;
        volatile uint32_t *const descriptor=(volatile uint32_t *)(uintptr_t)block;
        descriptor[0]=MSPI_BASE+(module<<12)+0x2b4u;
        descriptor[1]=0u;
        saved_mask=opencfw_bl_critical_save();
        status=opencfw_provider_4279f0(queue,1u);
        if(status!=0u){
            __asm__ volatile("msr primask, %0" :: "r"(saved_mask) : "memory");
            (void)opencfw_provider_4279be((uint32_t)(uintptr_t)queue);
            return status;
        }
        const uint32_t pending=handle[8]++;
        if(pending==0u){
            status=enable_queue(handle);
            if(status!=0u)return status;
        }
    }

    status=opencfw_provider_42790a(queue,3u,&block,&sequence);
    if(status!=0u)return status;
    volatile uint32_t *const descriptor=(volatile uint32_t *)(uintptr_t)block;
    const uint32_t second_base=MSPI_BASE+(module<<12)+0x2b8u;
    const uint32_t flags_base=first_stage?0x40u:0u;
    const uint32_t extra_flags=first_stage?0x400000u:0u;
    descriptor[0]=second_base;
    descriptor[2]=second_base;
    descriptor[4]=MSPI_BASE+(module<<12)+0x2b4u;
    descriptor[1]=opencfw_bl_control_stage_two_flags(
        (uint32_t)(uintptr_t)handle,flags_base+*(const uint32_t *)(const void *)(config+4));
    descriptor[3]=0x4000u;
    descriptor[5]=extra_flags|*(const uint32_t *)(const void *)(config+8);

    saved_mask=opencfw_bl_critical_save();
    status=config[0]!=0u ?
        opencfw_provider_427c12((uint32_t)(uintptr_t)queue,0u):
        opencfw_provider_4279f0(queue,0u);
    if(status!=0u){
        __asm__ volatile("msr primask, %0" :: "r"(saved_mask) : "memory");
        (void)opencfw_provider_4279be((uint32_t)(uintptr_t)queue);
        return status;
    }

    const uint32_t pending=handle[8]++;
    *(volatile uint8_t *)((uintptr_t)handle+0x82cu)=config[0]!=0u?2u:0u;
    __asm__ volatile("msr primask, %0" :: "r"(saved_mask) : "memory");
    if(pending==0u){
        status=enable_queue(handle);
        if(status!=0u)return status;
    }
    return 0u;
}

uint32_t opencfw_hal_mspi_control_transaction_request(uint32_t handle_address,
                                                       uint32_t request,
                                                       void *config)
{
    if((uint8_t)request==30u)
        return request30((uint32_t *)(uintptr_t)handle_address,
                         (const uint8_t *)config);
    return 0xeeee0003u;
}

void opencfw_bl_control_request_completion(uint32_t handle_address)
{
    volatile uint32_t *const handle=(volatile uint32_t *)(uintptr_t)handle_address;
    const uint32_t module=handle[1];
    handle[8]=handle[0x20c]+1u;
    handle[7]=0u;
    *(volatile uint8_t *)((uintptr_t)handle+0x834u)=1u;
    *(volatile uint32_t *)(uintptr_t)(MSPI_BASE+(module<<12)+0x2b4u)=0x40u;
}
