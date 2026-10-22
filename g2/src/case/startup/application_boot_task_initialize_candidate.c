/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ae96 task metadata, stack fill and initial frame.
 */
#include <stdint.h>
extern void case_boot_task_fill(uint32_t address,uint32_t count,uint8_t value);
extern void case_boot_task_link_reset(uint32_t link);
extern uint32_t case_boot_task_frame(uint32_t top,void (*entry)(void *),void *arg);
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x0800AE96 (case_boot_task_initialize) */
void case_boot_task_initialize(void (*entry)(void *),const char *name,
                               uint32_t stack_words,void *arg,uint32_t priority,
                               uint32_t *created,uint32_t storage,uint32_t flags)
{
    (void)flags;
    uint32_t stack_end=*(volatile uint32_t *)(uintptr_t)(storage+0x30u);
    case_boot_task_fill(stack_end,stack_words*4u,0xa5u);
    uint32_t top=(stack_end+(stack_words-1u)*4u)&~7u;
    if((top&7u)!=0u)native_fault();
    volatile uint8_t *record=(volatile uint8_t *)(uintptr_t)storage;
    if(name!=0){
        for(uint32_t i=0u;i<16u;++i){
            uint8_t byte=(uint8_t)name[i];record[0x34u+i]=byte;
            if(byte==0u)break;
        }
        record[0x43u]=0u;
    }else record[0x34u]=0u;
    if(priority>=56u)priority=55u;
    wr(storage+0x2cu,priority);wr(storage+0x4cu,priority);
    wr(storage+0x50u,0u);
    case_boot_task_link_reset(storage+4u);
    case_boot_task_link_reset(storage+24u);
    wr(storage+16u,storage);
    wr(storage+24u,56u-priority);
    wr(storage+36u,storage);
    wr(storage+84u,0u);
    record[0x58u]=0u;
    wr(storage,case_boot_task_frame(top,entry,arg));
    if(created!=0)*created=storage;
}
