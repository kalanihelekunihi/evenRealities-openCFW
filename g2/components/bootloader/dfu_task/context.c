/* SPDX-License-Identifier: MIT
 * Reconstructed 42dca2,42dd14,42dd70,42ddae,42ddda,42e1c4.
 * Raw failures deliberately preserve stock invalid-address write; not a
 * substitution for unknown functionality. Kernel/platform providers remain.
 */
#include "context.h"
#include <stddef.h>
#define THREAD (*(uint32_t volatile *)(uintptr_t)0x200004d4u)
#define QUEUE (*(uint32_t volatile *)(uintptr_t)0x200004d8u)
extern uint32_t opencfw_boot_dfu_queue_new(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_boot_dfu_queue_put(uint32_t,const void *,uint32_t,uint32_t);
extern uint32_t opencfw_boot_dfu_thread_new(uintptr_t,uintptr_t,const void *);
extern void opencfw_boot_dfu_thread_terminate(uint32_t);
extern uint32_t opencfw_boot_dfu_flags_set(uint32_t,uint32_t);
extern uint64_t opencfw_boot_dfu_flags_wait(uint32_t,uint32_t,uint32_t,uint32_t);
extern void opencfw_boot_dfu_panic(void);
extern void opencfw_boot_dfu_control_one(void);
extern void opencfw_boot_dfu_control_two(void);
extern void opencfw_boot_dfu_runtime_context(void);
extern void opencfw_boot_dfu_terminal(void);
/* Raw ARM32 CMSIS-style attribute words recovered at433048.
 * Exact wrapper revision still unverified; values not renamed as priorities
 * or security policy beyond the standard-compatible field positions. */
__attribute__((section(".boot_thread_name"),used))
const char opencfw_boot_dfu_thread_name[]="dfu";
static const uint32_t attributes[9]={0x4341a4u,0,0x20026b30u,0x70u,
    0x20020e00u,0x2000u,0x2eu,1u,0};
static void allocation_failure(void) {
    opencfw_boot_dfu_panic();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
    for(;;)__asm__ volatile("":::"memory");
}
void opencfw_boot_dfu_queue_init(void) {
    QUEUE=opencfw_boot_dfu_queue_new(50u,40u,0);
    if(!QUEUE)allocation_failure();
}
void opencfw_boot_dfu_thread_init(void) {
    THREAD=opencfw_boot_dfu_thread_new((uintptr_t)opencfw_boot_dfu_orchestrator,0,attributes);
    if(!THREAD)allocation_failure();
}
void opencfw_boot_dfu_thread_deinit(void) {
    if(THREAD){opencfw_boot_dfu_thread_terminate(THREAD);THREAD=0;}
}
uint32_t opencfw_boot_dfu_send(const opencfw_boot_dfu_message *message) {
    if(!QUEUE){opencfw_boot_dfu_log(1,0x164u);return 0;}
    uint32_t result=opencfw_boot_dfu_queue_put(QUEUE,message,0,0);
    if(!result)opencfw_boot_dfu_flags_set(THREAD,1u<<22);
    else opencfw_boot_dfu_log(1,0x169u);
    return result==0;
}
void opencfw_boot_dfu_dispatch(uint32_t flags) {
    if(flags&(1u<<22))opencfw_boot_dfu_task();
    if(flags&(1u<<23))opencfw_boot_dfu_terminal();
}
#ifdef OPENCFW_DFU_TASK_AT_STOCK_ADDRESS
__attribute__((section(".boot_dfu_orchestrator"),used))
#endif
void opencfw_boot_dfu_orchestrator(void) {
    opencfw_boot_dfu_control_one();
    opencfw_boot_dfu_queue_init();
    opencfw_boot_dfu_runtime_context();
    /* Stock noop callback42dd98 has no state or return value. */
    opencfw_boot_dfu_control_two();
    for(;;) {
        uint32_t flags=(uint32_t)opencfw_boot_dfu_flags_wait(0xffffffu,0,UINT32_MAX,0);
        if(flags && !(flags&(1u<<31)))opencfw_boot_dfu_dispatch(flags);
        else opencfw_boot_dfu_log(1,0x199u);
    }
}
