/* SPDX-License-Identifier: MIT
 * HAL control request 34 (0x22), queue descriptor transaction.
 */
#include "control_request_helpers.h"
#include "control_request34.h"
#include <stddef.h>
#include <stdint.h>

#define MSPI_BASE UINT32_C(0x40060000)

extern uint32_t opencfw_provider_42790a(uint32_t *queue,uint32_t blocks,
                                        uint32_t *block,uint32_t *sequence);
extern uint32_t opencfw_provider_4279f0(uint32_t *queue,uint32_t kind);
extern uint32_t opencfw_provider_4279be(uint32_t queue);
extern uint32_t opencfw_provider_427878(uint32_t *queue);
extern uint32_t opencfw_bl_critical_save(void);
extern uint32_t clock_request(uint32_t clock_id,uint32_t user_id);

void opencfw_bl_control_request34_noop(uint32_t unused)
{
    (void)unused;
}

static uint32_t enable_queue(uint32_t *handle)
{
    uint32_t status=clock_request(4u,(handle[1]+0x10u)&0xffu);
    if(status!=0u)return status;
    (void)opencfw_provider_427878((uint32_t *)(uintptr_t)handle[0x20a]);
    return 0u;
}

uint32_t opencfw_hal_mspi_control_request34(uint32_t handle_address,
                                            void *config_pointer)
{
    uint32_t *const handle=(uint32_t *)(uintptr_t)handle_address;
    const uint32_t *const config=(const uint32_t *)config_pointer;
    uint32_t *const queue=(uint32_t *)(uintptr_t)handle[0x20a];
    uint32_t block,sequence,status;
    uint32_t *cursor;
    uint32_t saved_mask;
    uint32_t callback;
    uint32_t old_pending;
    uint32_t count;
    uint32_t i;
    const uint32_t module=handle[1];

    if(config==NULL)return 6u;
    if(queue==NULL)return 7u;
    count=config[3];
    if(handle[8]==0x100u)return 5u;
    status=opencfw_provider_42790a(queue,count+3u,&block,&sequence);
    if(status!=0u)return 5u;

    cursor=(uint32_t *)(uintptr_t)block;
    const uint32_t command_reg=MSPI_BASE+(module<<12)+0x2b8u;
    cursor[0]=command_reg;
    cursor[1]=opencfw_bl_control_stage_two_flags(
        (uint32_t)(uintptr_t)handle,config[0]);
    cursor+=2;
    const uint32_t *const tuples=(const uint32_t *)(uintptr_t)config[2];
    for(i=0u;i<count;i++){
        cursor[0]=tuples[2u*i];
        cursor[1]=tuples[2u*i+1u];
        cursor+=2;
    }
    if(config[6]!=0u)
        *(uint32_t *)(uintptr_t)config[6]=(uint32_t)(uintptr_t)cursor;
    cursor[0]=command_reg;
    cursor[1]=0x4000u;
    cursor[2]=MSPI_BASE+(module<<12)+0x2b4u;
    cursor[3]=config[1];

    callback=config[4];
    if(callback==0u && handle[0x20e]==0u &&
       *(volatile uint8_t *)((uintptr_t)handle+0x82cu)==0u &&
       handle[0x217]>=(handle[0x216]>>1))
        callback=(uint32_t)(uintptr_t)&opencfw_bl_control_request34_noop;
    handle[0x0au+(sequence&0xffu)]=callback;
    handle[0x10au+(sequence&0xffu)]=config[5];

    saved_mask=opencfw_bl_critical_save();
    status=opencfw_provider_4279f0(queue,callback!=0u);
    if(status!=0u){
        __asm__ volatile("msr primask, %0" :: "r"(saved_mask) : "memory");
        (void)opencfw_provider_4279be((uint32_t)(uintptr_t)queue);
        return status;
    }

    old_pending=handle[8]++;
    handle[0x20c]++;
    if(config[4]!=0u){
        *(volatile uint8_t *)((uintptr_t)handle+0x82du)=0u;
        handle[0x217]=0u;
    }else if(callback!=0u || saved_mask!=0u){
        handle[0x217]=0u;
    }else{
        handle[0x217]++;
    }
    __asm__ volatile("msr primask, %0" :: "r"(saved_mask) : "memory");
    if(old_pending==0u)return enable_queue(handle);
    return 0u;
}

uint32_t opencfw_hal_mspi_control_request34_dispatch(uint32_t handle,
                                                      uint32_t request,
                                                      void *config)
{
    if((uint8_t)request!=34u)return 0xeeee0004u;
    return opencfw_hal_mspi_control_request34(handle,config);
}
