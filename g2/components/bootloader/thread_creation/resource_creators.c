/* SPDX-License-Identifier: MIT. Reconstructed timer constructors4163b2,
 * 4192a8/4192de/419326 and mutex constructors416610/419da8/419dc2/419d8a.
 * Private ARM32 layouts; callback addresses are serialized stock addresses.
 */
#include "resource_creators.h"
#include <stddef.h>
#include "queue_receive.h"
#include "queue_send.h"
extern uint32_t opencfw_bl_context_guard(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern uintptr_t opencfw_bl_rtos_allocate(uint32_t);
extern void opencfw_bl_rtos_free(uintptr_t);
extern void opencfw_boot_timer_initialize(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern uint32_t opencfw_boot_timer_queue_fresh(uint32_t,uint32_t,uintptr_t,uintptr_t,uint32_t);
static _Noreturn void fatal(void) {
    (void)opencfw_bl_mask_interrupts();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
    for (;;) __asm__ volatile("b ." ::: "memory");
}
/* 4196c2 and41639a: callback record is timer ID with its low allocation bit
 * removed. The assembly wrapper retains the original saved-R7 return ABI. */
uintptr_t opencfw_boot_timer_id_get(uint32_t *timer) {
    if (!timer)fatal();
    opencfw_bl_kernel_enter();uintptr_t id=timer[7];
    opencfw_bl_kernel_exit();return id;
}
__attribute__((naked))
void opencfw_boot_timer_callback_dispatcher(uint32_t *timer __attribute__((unused))) {
    __asm__ volatile(
        "push {r7, lr}\n"
        "bl opencfw_boot_timer_id_get\n"
        "movs r1, r0\n"
        "lsrs r1, r1, #1\n"
        "lsls r1, r1, #1\n"
        "cmp r1, #0\n"
        "beq 1f\n"
        "ldr r0, [r1, #4]\n"
        "ldr r1, [r1]\n"
        "blx r1\n"
        "1: pop {r0, pc}\n");
}
void opencfw_boot_timer_object_initialize(uintptr_t name,uint32_t period,
    uint32_t periodic,uintptr_t id,uintptr_t callback,uint32_t *timer) {
    if (!period)fatal();
    opencfw_boot_timer_initialize();
    timer[0]=name;timer[6]=period;timer[7]=id;timer[8]=callback;
    timer[5]=0;
    if (periodic)((uint8_t *)timer)[40]|=4;
}
uintptr_t opencfw_boot_timer_create_dynamic(uintptr_t name,uint32_t period,
    uint32_t periodic,uintptr_t id,uintptr_t callback) {
    uint32_t *timer=(uint32_t *)opencfw_bl_rtos_allocate(44);
    if (timer) {
        ((uint8_t *)timer)[40]=0;
        opencfw_boot_timer_object_initialize(name,period,periodic,id,callback,timer);
    }
    return (uintptr_t)timer;
}
uintptr_t opencfw_boot_timer_create_static(uintptr_t name,uint32_t period,
    uint32_t periodic,uintptr_t id,uintptr_t callback,uint32_t *timer) {
    if (!timer)fatal();
    ((uint8_t *)timer)[40]=2;
    opencfw_boot_timer_object_initialize(name,period,periodic,id,callback,timer);
    return (uintptr_t)timer;
}
uintptr_t opencfw_provider_4163b2(uintptr_t callback,uint32_t type,
    uintptr_t argument,const uint32_t *attr) {
    if (opencfw_bl_context_guard() || !callback)return 0;
    uintptr_t record=0;uint32_t allocated=0;
    if (attr && attr[2] && attr[3]>=52)record=attr[2]+44;
    if (!record) {
        record=opencfw_bl_rtos_allocate(8);
        if (record)allocated=1;
    }
    if (!record)return 0;
    ((uint32_t *)record)[0]=callback;((uint32_t *)record)[1]=argument;
    uint32_t periodic=(uint8_t)type!=0;
    uintptr_t name=attr?attr[0]:0;
    int32_t mode=0;
    if (attr)mode=(attr[2] && attr[3]>=44)?1:
        (!attr[2] && !attr[3])?0:-1;
    uintptr_t tagged=record|allocated,result=0;
    if (mode==1)result=opencfw_boot_timer_create_static(name,1,periodic,
        tagged,0x41639b,(uint32_t *)(uintptr_t)attr[2]);
    else if (!mode)result=opencfw_boot_timer_create_dynamic(name,1,periodic,
        tagged,0x41639b);
    if (!result && allocated)opencfw_bl_rtos_free(tagged&~(uintptr_t)1);
    return result;
}
void opencfw_boot_mutex_object_initialize(uint32_t *queue) {
    if (!queue)return;
    queue[2]=0;queue[0]=0;queue[3]=0;
    (void)opencfw_bl_kernel_queue_put_blocking(queue,0,0,0);
}
uintptr_t opencfw_boot_mutex_create_dynamic(uint32_t type) {
    uintptr_t queue=opencfw_bl_kernel_queue_create_dynamic(1,0,(uint8_t)type);
    opencfw_boot_mutex_object_initialize((uint32_t *)queue);return queue;
}
uintptr_t opencfw_boot_mutex_create_static(uint32_t type,uint32_t *storage) {
    uintptr_t queue=opencfw_boot_timer_queue_fresh(1,0,0,(uintptr_t)storage,(uint8_t)type);
    opencfw_boot_mutex_object_initialize((uint32_t *)queue);return queue;
}
uintptr_t opencfw_provider_416610(const uint32_t *attr) {
    if (opencfw_bl_context_guard())return 0;
    uint32_t bits=attr?attr[1]:0,recursive=bits&1;
    if (bits&8)return 0;
    int32_t mode=attr?((attr[2] && attr[3]>=80)?1:
        (!attr[2] && !attr[3])?0:-1):0;
    uintptr_t result=0;
    if (mode==1)result=opencfw_boot_mutex_create_static(recursive?4:1,
        (uint32_t *)(uintptr_t)attr[2]);
    else if (!mode)result=opencfw_boot_mutex_create_dynamic(recursive?4:1);
    if (result && recursive)result|=1;
    return result;
}
