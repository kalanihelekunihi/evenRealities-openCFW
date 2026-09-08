/* SPDX-License-Identifier: MIT */
/* Candidate only: observed asynchronous submission, fixed GRUS layout.
 * The complete shared driver state is not yet source-owned. */
#include <stdint.h>
#include <stddef.h>
#include <driver/gx_snpu.h>
_Static_assert(sizeof(GX_SNPU_TASK)==32,"GRUS task ABI");
_Static_assert(offsetof(GX_SNPU_TASK,cmd)==20,"GRUS command field");
extern volatile uint32_t open_cfw_gx8002_snpu_run_words[0x5e0/4];
extern int open_cfw_gx8002_snpu_resume_internal(void);
extern void open_cfw_gx8002_snpu_submit_task(void *);
static inline uint32_t read_word(uint32_t offset)
{
    return *(volatile uint32_t *)((uintptr_t)open_cfw_gx8002_snpu_run_words+offset);
}
static inline void write_word(uint32_t offset,uint32_t value)
{
    *(volatile uint32_t *)((uintptr_t)open_cfw_gx8002_snpu_run_words+offset)=value;
}
int open_cfw_gx8002_snpu_run_task(GX_SNPU_TASK *task,
                               GX_SNPU_CALLBACK callback,void *private_data)
{
    if (!task || !read_word(0x5c4)) return -1;
    uint32_t next=read_word(0x5b4)+1u;
    if ((uint32_t)((int32_t)next%10)==read_word(0x5b0)) return -1;
    uint32_t offset=read_word(0x5b4)*144u;
    volatile uint32_t *record=(volatile uint32_t *)((uintptr_t)open_cfw_gx8002_snpu_run_words+offset);
    void *descriptor=(void *)((uintptr_t)record+16u);
    record[0x90/4]=(uint32_t)(uintptr_t)callback;
    int module_id=task->module_id;
    record[0x98/4]=(uint32_t)(uintptr_t)private_data;
    record[0x28/4]=(uint32_t)(uintptr_t)task->ops;
    record[0x34/4]=(uint32_t)(uintptr_t)task->data;
    record[0x94/4]=(uint32_t)module_id;
    void *input=task->input;
    void *command=task->cmd;
    record[0x40/4]=(uint32_t)(uintptr_t)command;
    record[0x4c/4]=(uint32_t)(uintptr_t)input;
    record[0x58/4]=(uint32_t)(uintptr_t)task->output;
    record[0x64/4]=(uint32_t)(uintptr_t)task->tmp_mem;
    record[0x70/4]=(uint32_t)(uintptr_t)task->weight;
    uint32_t bus_descriptor=(uint32_t)(uintptr_t)descriptor & UINT32_C(0x0fffffff);
    record[0x7c/4]=bus_descriptor;
    /* Base slot 8: inferred 32-bit immediate-operand sentinel. The pinned
     * gxDNN host model selects embedded operands when a resolved pointer
     * equals -2. Target-width mapping still needs corroboration. */
    record[0x88/4]=UINT32_MAX-1u;
    /* Completion interrupt, absolute link, idle opcode. */
    record[0x10/4]=(1u<<22)|(1u<<16)|0xffu;
    record[0x14/4]=bus_descriptor;
    record[0x84/4]=(uint32_t)(uintptr_t)command;
    next=read_word(0x5b4)+1u;
    write_word(0x5b4,(uint32_t)((int32_t)next%10));
    if (read_word(0)==GX_SNPU_STALL) open_cfw_gx8002_snpu_resume_internal();
    open_cfw_gx8002_snpu_submit_task(descriptor);
    return 0;
}
