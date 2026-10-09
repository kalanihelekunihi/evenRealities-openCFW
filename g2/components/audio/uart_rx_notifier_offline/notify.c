/* Reconstructed valid-task, index0 stock ISR notifier0x455DC0.
 * No exception delivery, context-switch implementation or full RTOS claim. */
#include <stdint.h>
#include "notify.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t offline_mask_set(void);
extern void offline_mask_restore(uint32_t);
static void remove_item(uint32_t item){
    uint32_t list=W(item+16),next=W(item+4),prev=W(item+8);
    W(next+8)=prev;W(prev+4)=next;
    if(W(list+4)==item)W(list+4)=prev;
    W(item+16)=0;W(list)=W(list)-1;
}
static void insert_end(uint32_t list,uint32_t item){
    uint32_t index=W(list+4);
    W(item+4)=index;W(item+8)=W(index+8);
    W(W(index+8)+4)=item;W(index+8)=item;
    W(item+16)=list;W(list)=W(list)+1;
}
uint32_t uart_notify_isr(uint32_t task,uint32_t index,uint32_t value,uint32_t action,uint32_t *previous,uint32_t *woken){
    /* Invalid pointer/index assertion paths deliberately outside contract. */
    if(!task||index)return 0;
    uint32_t oldmask=offline_mask_set(),result=1;
    if(previous)*previous=W(task+104);
    uint32_t oldstate=B(task+108);B(task+108)=2;
    switch((uint8_t)action){
    case 0:break;
    case 1:W(task+104)|=value;break;
    case 2:W(task+104)=W(task+104)+1;break;
    case 3:W(task+104)=value;break;
    case 4:if(oldstate==2)result=0;else W(task+104)=value;break;
    default:break; /* invalid-action assertion configuration unvalidated */
    }
    if(oldstate==1){
        /* Stock asserts event-item containerNULL before the following paths. */
        if(W(0x20074a58)==0){
            remove_item(task+4);
            uint32_t priority=W(task+44);
            if(W(0x20074a38)<priority)W(0x20074a38)=priority;
            insert_end(0x2006a49c+20*priority,task+4);
        }else insert_end(0x20073d24,task+24);
        if(W(W(0x20074a20)+44)<W(task+44)){
            if(woken)*woken=1;
            W(0x20074a44)=1;
        }
    }
    offline_mask_restore(oldmask);return result;
}
