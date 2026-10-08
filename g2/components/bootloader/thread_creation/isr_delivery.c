/* SPDX-License-Identifier: MIT. Independently reconstructed from locked
 * f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5.
 * ISR queue copies/wakes, single-slot notify and deferred flags enqueue.
 * No allocation, pointer retain/release or cancellation is invented. */
#include "isr_delivery.h"
#include "queue_send.h"
#include "queue_receive.h"
#include "timer_wait.h"
#include "event_flags_set.h"
#include <stddef.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_restore_interrupts(uint32_t mask);
extern uint32_t opencfw_bl_remove_event_waiter(uint32_t *);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_kernel_reschedule(void);
extern void opencfw_boot_list_initialize(uint32_t *);
static _Noreturn void fail(void) {
    (void)opencfw_bl_mask_interrupts();W(UINT32_MAX)=0;
    for (;;) __asm__ volatile("b .":::"memory");
}
uint32_t opencfw_boot_queue_isr_task_count(void) {return W(0x20027144);}
static void lock_increment(volatile int8_t *lock,int8_t previous) {
    if((uint32_t)(int32_t)previous<opencfw_boot_queue_isr_task_count()) {
        if(previous==127)fail();
        *lock=(int8_t)(previous+1);
    }
}
uint32_t opencfw_bl_kernel_queue_put_from_isr(uint32_t *queue,const void *message,uint32_t *woken,uint32_t mode) {
    if(!queue || (!message && queue[16]) || (mode==2 && queue[15]!=1))fail();
    uint32_t mask=opencfw_bl_mask_interrupts(),result=0;
    if(queue[14]<queue[15] || mode==2) {
        volatile int8_t *lock=(volatile int8_t *)queue+0x45;int8_t previous=*lock;
        (void)opencfw_boot_queue_copy_in(queue,message,mode);
        if(previous==-1) {
            if(queue[9] && opencfw_bl_remove_event_waiter(queue+9) && woken)*woken=1;
        } else lock_increment(lock,previous);
        result=1;
    }
    opencfw_bl_restore_interrupts(mask);return result;
}
uint32_t opencfw_bl_kernel_queue_get_from_isr(uint32_t *queue,void *message,uint32_t *woken) {
    if(!queue || (!message && queue[16]))fail();
    uint32_t mask=opencfw_bl_mask_interrupts(),result=0,count=queue[14];
    if(count) {
        volatile int8_t *lock=(volatile int8_t *)queue+0x44;int8_t previous=*lock;
        opencfw_boot_queue_copy_out(queue,message);queue[14]=count-1;
        if(previous==-1) {
            if(queue[4] && opencfw_bl_remove_event_waiter(queue+4) && woken)*woken=1;
        } else lock_increment(lock,previous);
        result=1;
    }
    opencfw_bl_restore_interrupts(mask);return result;
}
static void append(uint32_t *list,uint32_t *item) {
    uint32_t *anchor=(uint32_t *)(uintptr_t)list[1];
    uint32_t *previous=(uint32_t *)(uintptr_t)anchor[2];
    item[1]=(uint32_t)(uintptr_t)anchor;item[2]=(uint32_t)(uintptr_t)previous;
    previous[1]=(uint32_t)(uintptr_t)item;anchor[2]=(uint32_t)(uintptr_t)item;
    item[4]=(uint32_t)(uintptr_t)list;list[0]++;
}
uint32_t opencfw_boot_isr_thread_notify(uint32_t *thread,uint32_t index,uint32_t value,uint32_t action,uint32_t *previous,uint32_t *woken) {
    if(!thread || index)fail();
    uint32_t result=1,mask=opencfw_bl_mask_interrupts();
    if(previous)*previous=thread[26];
    uint8_t *state=(uint8_t *)thread+0x6c;uint8_t old=*state;*state=2;
    switch((uint8_t)action) {
    case 0:break;
    case 1:thread[26]|=value;break;
    case 2:thread[26]++;break;
    case 3:thread[26]=value;break;
    case 4:if(old!=2)thread[26]=value;else result=0;break;
    default:if(W(0x20027148))fail();break;
    }
    if(old==1) {
        if(thread[10])fail();
        if(!W(0x2002716c)) {
            (void)opencfw_boot_list_unlink(thread+1);
            if(W(0x2002714c)<thread[11])W(0x2002714c)=thread[11];
            append((uint32_t *)(uintptr_t)(0x20024870+20*thread[11]),thread+1);
        } else append((uint32_t *)(uintptr_t)0x20026f5c,thread+6);
        uint32_t *current=(uint32_t *)(uintptr_t)W(0x20027134);
        if(current[11]<thread[11]) {
            if(woken)*woken=1;
            W(0x20027158)=1;
        }
    }
    opencfw_bl_restore_interrupts(mask);return result;
}
uint32_t opencfw_boot_pend_callback_isr(void (*callback)(uint32_t,uint32_t),uint32_t argument,uint32_t value,uint32_t *woken) {
    uint32_t message[4]={0xfffffffeu,(uint32_t)(uintptr_t)callback,argument,value};
    return opencfw_bl_kernel_queue_put_from_isr((uint32_t *)(uintptr_t)W(0x20027180),message,woken,0);
}
void opencfw_boot_event_flags_deferred(uint32_t argument,uint32_t flags) {
    (void)opencfw_boot_event_flags_set((uint32_t *)(uintptr_t)argument,flags);
}
uint32_t opencfw_bl_event_flags_set_isr(uint32_t *event,uint32_t flags,uint32_t *woken) {
    return opencfw_boot_pend_callback_isr(opencfw_boot_event_flags_deferred,(uint32_t)(uintptr_t)event,flags,woken);
}
uint32_t opencfw_boot_kernel_queue_reset(uint32_t *queue,uint32_t is_new) {
    if(!queue || !queue[15] || UINT32_MAX/queue[15]<queue[16])fail();
    opencfw_bl_kernel_enter();
    queue[2]=queue[0]+queue[15]*queue[16];queue[14]=0;
    queue[1]=queue[0];queue[3]=queue[0]+(queue[15]-1)*queue[16];
    ((volatile int8_t *)queue)[0x44]=-1;((volatile int8_t *)queue)[0x45]=-1;
    if(is_new){opencfw_boot_list_initialize(queue+4);opencfw_boot_list_initialize(queue+9);}
    else if(queue[4] && opencfw_bl_remove_event_waiter(queue+4))opencfw_bl_kernel_reschedule();
    opencfw_bl_kernel_exit();return 1;
}
