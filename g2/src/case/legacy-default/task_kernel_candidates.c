/* SPDX-License-Identifier: MIT
 * Stock 0x0800cde4 task flag lookup and 0x0800cd80 queue signal routing.
 * Kernel critical sections and queue scheduler remain named contracts.
 */
#include <stdint.h>
extern void case_kernel_enter(void); /* 0x0800bffc */
extern void case_kernel_exit(void);  /* 0x0800c014 */
extern uint32_t case_kernel_mode(void); /* 0x0800ca4c */
extern uint32_t case_kernel_queue_send(uint32_t queue,const uint32_t *event,
                                       uint32_t timeout,uint32_t mode); /* 0x0800c686 */
extern uint32_t case_kernel_queue_post(uint32_t queue,const void *event,
                                       uint32_t *woken,uint32_t mode); /* 0x0800c7a8 */
uint32_t case_task_lookup(uint32_t handle)
{
    /* The 0xab26 caller rejects zero before this entry. */
    case_kernel_enter();
    uint32_t flags=*(volatile uint8_t *)(uintptr_t)(handle+0x28u);
    case_kernel_exit();
    return flags&1u;
}
uint32_t case_task_signal(uint32_t handle,uint32_t event,
                          uint32_t a,uint32_t b,uint32_t c)
{
    uint32_t queue=*(volatile uint32_t *)(uintptr_t)0x20000164u;
    if(queue==0u)return 0u;
    uint32_t message[3]={event,a,handle};
    if((int32_t)event<6){
        if(case_kernel_mode()==2u)
            return case_kernel_queue_send(queue,message,c,0u);
        return case_kernel_queue_send(queue,message,0u,0u);
    }
    return case_kernel_queue_post(queue,message,(uint32_t *)(uintptr_t)b,0u);
}
