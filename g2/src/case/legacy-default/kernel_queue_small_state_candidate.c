/* SPDX-License-Identifier: MIT
 * Stock 0x0800b080, 0x0800c15c and 0x0800c380. The scheduler state
 * base is the retained image's shared RAM literal 0x20000128.
 */
#include <stdint.h>
extern void case_kernel_enter(void);
extern void case_kernel_exit(void);
extern _Noreturn void case_kernel_invariant_failure(uint32_t condition);

uint32_t case_queue_is_active(uint32_t queue)
{
    const volatile uint32_t *words=(const volatile uint32_t *)(uintptr_t)queue;
    case_kernel_enter();
    uint32_t used=words[0x38u/4u];
    uint32_t capacity=words[0x3cu/4u];
    case_kernel_exit();
    return used==capacity;
}

void case_kernel_timeout_start(uint32_t *snapshot)
{
    const volatile uint32_t *state=(const volatile uint32_t *)(uintptr_t)0x20000128u;
    snapshot[0]=state[0x20u/4u];
    snapshot[1]=state[0x0cu/4u];
}

void case_kernel_scheduler_suspend(void)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000128u;
    state[0x30u/4u]++;
}

uint32_t case_kernel_timeout_check(uint32_t snapshot[2],uint32_t *ticks)
{
    if(snapshot==0 || ticks==0)case_kernel_invariant_failure(8u);
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000128u;
    case_kernel_enter();
    uint32_t elapsed=state[0x0cu/4u]-snapshot[1];
    uint32_t result;
    if(*ticks==0xffffffffu)result=0u;
    else if(snapshot[0]==state[0x20u/4u] || state[0x0cu/4u]<snapshot[1]){
        if(elapsed<*ticks){
            *ticks-=elapsed;
            case_kernel_timeout_start(snapshot);
            result=0u;
        }else{*ticks=0u;result=1u;}
    }else result=1u;
    case_kernel_exit();
    return result;
}
