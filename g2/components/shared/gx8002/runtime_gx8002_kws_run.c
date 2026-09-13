/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip LvpKwsRun at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, lvp/common/snpu_engine/lvp_kws.c.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd.
 * See NATIONALCHIP-STREAM-NOTICE.txt. Recovered stock configuration:
 * 40 features/frame, 13-frame window, RNN state output, cycle stats disabled. */
#include <stdint.h>
#include <stddef.h>
#include <driver/gx_snpu.h>
#include <lvp_context.h>
extern void *LvpGetFeatsBuffer(void);
extern void *LvpGetLogfbankBuffer(LVP_CONTEXT *,unsigned);
extern int LvpGetPcmFrameNumPerContext(void);
extern void gx_dcache_invalid_range(uint32_t *,int);
extern void gx_dcache_clean_range(uint32_t *,int);
extern void *memmove(void *,const void *,size_t);
extern void *memcpy(void *,const void *,size_t);
extern int LvpGetContext(unsigned,LVP_CONTEXT **,unsigned *);
extern int LvpCTCModelInitSnpuTask(GX_SNPU_TASK *);
extern void *LvpCTCModelGetSnpuFeatsBuffer(void *);
extern void *LvpCTCModelGetSnpuStateBuffer(void *);
extern unsigned LvpCTCModelGetSnpuFeatsDim(void);
extern int open_cfw_gx8002_audio_completion_forward(int,GX_SNPU_STATE,void *);
_Static_assert(offsetof(LVP_CONTEXT,ctx_index)==8,"context index ABI");
_Static_assert(offsetof(LVP_CONTEXT,snpu_buffer)==16,"context buffer ABI");
int open_cfw_gx8002_kws_run(LVP_CONTEXT *context)
{
    if (!context) return -1;
    short *input=LvpGetFeatsBuffer();
    short *current=LvpGetLogfbankBuffer(context,context->ctx_index);
    unsigned stride=LvpGetPcmFrameNumPerContext();
    unsigned incoming=stride*80u, retained=(13u-stride)*80u;
    gx_dcache_invalid_range((uint32_t *)current,(int)incoming);
    memmove(input,(uint8_t *)input+incoming,retained);
    memcpy((uint8_t *)input+retained,current,incoming);
    memcpy(context->snpu_buffer,input,1040);
    gx_dcache_clean_range(context->snpu_buffer,1040);
    GX_SNPU_TASK task;
    LVP_CONTEXT *previous,*next;
    unsigned size;
    LvpGetContext(context->ctx_index,&previous,&size);
    LvpGetContext(context->ctx_index+1u,&next,&size);
    LvpCTCModelInitSnpuTask(&task);
    short *features=LvpCTCModelGetSnpuFeatsBuffer(previous->snpu_buffer);
    short *output=LvpCTCModelGetSnpuStateBuffer(next->snpu_buffer);
    gx_dcache_clean_range((uint32_t *)features,(int)(LvpCTCModelGetSnpuFeatsDim()*2u));
    task.input=(void *)((uintptr_t)features&0x0fffffffu);
    task.output=(void *)((uintptr_t)output&0x0fffffffu);
    gx_snpu_run_task(&task,open_cfw_gx8002_audio_completion_forward,next);
    return 0;
}
