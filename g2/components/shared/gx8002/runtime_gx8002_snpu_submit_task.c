/* SPDX-License-Identifier: MIT */
/* Recovered command-chain publication; see the decoded submission/cache checks. */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_snpu_submit_words[0x5e0/4];
extern void open_cfw_gx8002_npu_set_task_head(void *,uint32_t);
extern uint32_t open_cfw_gx8002_npu_get_over_cmd_addr(void *,uint32_t *);
extern void open_cfw_gx8002_npu_enable(void *);
extern void open_cfw_gx8002_snpu_task_cmd_cache_flush(void *);
extern void open_cfw_gx8002_dcache_clean_range(void *,int32_t);
static inline uint32_t read_word(uint32_t offset)
{ return open_cfw_gx8002_snpu_submit_words[offset/4]; }
static inline void write_word(uint32_t offset,uint32_t value)
{ open_cfw_gx8002_snpu_submit_words[offset/4]=value; }
static inline void *registers(void)
{ return (void *)(uintptr_t)read_word(0x5c4); }
void open_cfw_gx8002_snpu_submit_task(void *descriptor)
{
    uint32_t command=(uint32_t)(uintptr_t)descriptor+16u;
    uint32_t head=command&UINT32_C(0x0fffffff);
    if (!read_word(0x5c0)) {
        write_word(0,1);
    } else if (read_word(0)==2) {
        uint32_t completed;
        open_cfw_gx8002_npu_get_over_cmd_addr(registers(),&completed);
        if (completed) {
            *(volatile uint32_t *)(uintptr_t)(read_word(0x5c0)+4u)=head;
            head=*(volatile uint32_t *)(uintptr_t)(completed+UINT32_C(0x20000004));
        }
        write_word(0,1);
    } else {
        open_cfw_gx8002_snpu_task_cmd_cache_flush(descriptor);
        void *previous=(void *)(uintptr_t)read_word(0x5c0);
        *(volatile uint32_t *)((uintptr_t)previous+4)=head;
        open_cfw_gx8002_dcache_clean_range(previous,8);
        goto finish;
    }
    open_cfw_gx8002_npu_set_task_head(registers(),head);
    open_cfw_gx8002_snpu_task_cmd_cache_flush(descriptor);
    open_cfw_gx8002_npu_enable(registers());
finish:
    write_word(0x5c0,(uint32_t)(uintptr_t)descriptor);
}
