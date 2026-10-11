/* SPDX-License-Identifier: MIT
 * Stock 0x0800bffc / 0x0800c014 nested interrupt gate and 0x0800ca4c
 * scheduler mode read. Underflow is an explicit invalid-state contract.
 */
#include <stdint.h>
extern void case_kernel_nesting_underflow(void);
void case_kernel_enter(void)
{
    volatile uint32_t *depth=(volatile uint32_t *)(uintptr_t)0x2000019cu;
    __asm__ volatile("cpsid i" ::: "memory");
    *depth+=1u;
    __asm__ volatile("dsb 0xf\n\tisb 0xf" ::: "memory");
}
void case_kernel_exit(void)
{
    volatile uint32_t *depth=(volatile uint32_t *)(uintptr_t)0x2000019cu;
    if(*depth==0u){case_kernel_nesting_underflow();return;}
    uint32_t next=*depth-1u;
    *depth=next;
    if(next==0u)__asm__ volatile("cpsie i" ::: "memory");
}
uint32_t case_kernel_mode(void)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000128u;
    if(state[0x14u/4u]==0u)return 1u;
    if(state[0x30u/4u]!=0u)return 0u;
    return 2u;
}
