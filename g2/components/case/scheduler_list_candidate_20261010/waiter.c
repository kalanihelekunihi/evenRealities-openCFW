#include "list_abi.h"

/* ARMv6-M FreeRTOS list item: value,+0; next,+4; previous,+8;
 * owner,+12; container,+16. List: count,+0; index,+4; sentinel,+8. */
uint32_t case_source_list_remove(case_item *item)
{
    case_list *list=item->container;
    item->previous->next=item->next;
    item->next->previous=item->previous;
    if(list->index==item)list->index=item->next;
    item->container=0;
    return --list->count;
}

void case_source_list_insert_end(case_list *list,case_item *item)
{
    case_item *index=list->index;
    item->next=index;
    item->previous=index->previous;
    index->previous->next=item;
    index->previous=item;
    item->container=list;
    ++list->count;
}

/* Source-bound 0x0800cba0. Caller owns a nonempty event list and valid
 * current TCB/list links. Null owner follows the original fatal path. */
int32_t case_remove_waiter(case_list *event_list)
{
    case_tcb *task=(case_tcb *)event_list->end.next->owner;
    if(!task){__asm volatile("cpsid i" ::: "memory");for(;;)__asm volatile("");}
    case_source_list_remove(&task->event_item);
    volatile uint32_t *state=(volatile uint32_t *)0x20000128u;
    if(state[12]==0u){
        case_source_list_remove(&task->state_item);
        uint32_t priority=task->priority;
        if(state[4]<priority)state[4]=priority;
        case_source_list_insert_end((case_list *)(0x20000ff4u+priority*20u),&task->state_item);
    }else{
        case_source_list_insert_end((case_list *)0x2000147cu,&task->event_item);
    }
    if(task->priority>((case_tcb *)state[0])->priority){state[7]=1u;return 1;}
    return 0;
}
