/* SPDX-License-Identifier: MIT */
/* Candidate recovery of diagnostics and restart ordering. State views and
 * command-address validity require separate qualification. */
#include <stdint.h>
extern int printf(const char *, ...);
#define MESSAGE(name,text) const char name[] __attribute__((section(".rodata." #name),used,aligned(1)))=text
MESSAGE(open_cfw_snpu_dump_word,"0x%08x ");
MESSAGE(open_cfw_snpu_overtime_addresses,"[SNPU] overtime addr: 0x%x, base cmd addr: 0x%x, prev int addr: 0x%x\n");
MESSAGE(open_cfw_snpu_overtime_before,"[SNPU] overtime addr - 0x80:\n");
MESSAGE(open_cfw_snpu_overtime_command,"[SNPU] overtime cmd :\n");
MESSAGE(open_cfw_snpu_overtime_type,"cmd_type: 0x%x\n");
extern const char open_cfw_gx8002_max_list_newline[];
extern volatile uint32_t open_cfw_snpu_overtime_words[0x5e0/4];
extern uint32_t open_cfw_gx8002_npu_get_base_addr(void *,uint32_t,uint32_t *);
extern uint32_t open_cfw_gx8002_npu_get_cur_cmd_addr(void *,uint32_t *);
extern uint32_t open_cfw_gx8002_npu_get_over_cmd_addr(void *,uint32_t *);
extern uint32_t open_cfw_gx8002_npu_get_task_head(void *,uint32_t *);
extern void open_cfw_gx8002_npu_disable(void *);
extern void open_cfw_gx8002_npu_reset(void *);
extern void open_cfw_gx8002_npu_regs_init(void);
extern void open_cfw_gx8002_npu_set_task_head(void *,uint32_t);
extern void open_cfw_gx8002_npu_enable(void *);
static inline void *state_pointer(uint32_t offset)
{ return (void *)(uintptr_t)open_cfw_snpu_overtime_words[offset/4]; }
int open_cfw_gx8002_snpu_dump_words(volatile uint32_t *address)
{
    unsigned int remaining=10;
    for (int i=1;i<=32;++i) {
        printf(open_cfw_snpu_dump_word,(unsigned int)*address);
        if (--remaining==0) {
            printf(open_cfw_gx8002_max_list_newline);
            remaining=10;
        }
        ++address;
    }
    return printf(open_cfw_gx8002_max_list_newline);
}
void open_cfw_gx8002_snpu_overtime_reset(void)
{
    uint32_t base,current,previous,head;
    open_cfw_gx8002_npu_get_base_addr(state_pointer(0x5cc),2,&base);
    open_cfw_gx8002_npu_get_cur_cmd_addr(state_pointer(0x5c4),&current);
    open_cfw_gx8002_npu_get_over_cmd_addr(state_pointer(0x5c4),&previous);
    uintptr_t mapped=(uintptr_t)(current+UINT32_C(0x20000000));
    printf(open_cfw_snpu_overtime_addresses,(unsigned int)current,(unsigned int)base,(unsigned int)previous);
    printf(open_cfw_snpu_overtime_before);
    open_cfw_gx8002_snpu_dump_words((volatile uint32_t *)(mapped-128u));
    printf(open_cfw_snpu_overtime_command);
    open_cfw_gx8002_snpu_dump_words((volatile uint32_t *)mapped);
    printf(open_cfw_snpu_overtime_type,(unsigned int)*(const uint8_t *)mapped);
    if (previous==0)
        open_cfw_gx8002_npu_get_task_head(state_pointer(0x5c4),&head);
    else
        head=((const uint32_t *)(uintptr_t)(previous+UINT32_C(0x20000000)))[1];
    open_cfw_gx8002_npu_disable(state_pointer(0x5c4));
    open_cfw_gx8002_npu_reset(state_pointer(0x5c8));
    open_cfw_gx8002_npu_regs_init();
    open_cfw_gx8002_npu_set_task_head(state_pointer(0x5c4),head);
    open_cfw_gx8002_npu_enable(state_pointer(0x5c4));
}
