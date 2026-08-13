/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <string.h>
#include "../../components/shared/freertos/runtime_freertos_task_priority_set.h"

static struct open_cfw_freertos_priority_set_tcb host_current, host_other;
static struct open_cfw_freertos_queue_next_list host_ready[56];
static uint32_t host_top, host_enter, host_exit, host_yield, host_remove, host_irq;

#undef OPEN_CFW_FREERTOS_PRIORITY_SET_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_PRIORITY_SET_CURRENT_TCB_LOAD() (&host_current)
#undef OPEN_CFW_FREERTOS_PRIORITY_SET_READY_LIST
#define OPEN_CFW_FREERTOS_PRIORITY_SET_READY_LIST(priority) (&host_ready[(priority)])
#undef OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_LOAD
#define OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_LOAD() (host_top)
#undef OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_STORE
#define OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_STORE(value) (host_top=(value))
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(condition) do { if (!(condition)) __builtin_trap(); } while(0)

void open_cfw_freertos_port_enter_critical(void){++host_enter;}
void open_cfw_freertos_port_exit_critical(void){++host_exit;}
void open_cfw_freertos_port_yield(void){++host_yield;}
unsigned open_cfw_freertos_list_remove(struct open_cfw_freertos_queue_next_list_item *item)
{++host_remove;if(item->container!=0)--item->container->item_count;item->container=0;return 0;}
#include "../../components/shared/freertos/runtime_freertos_task_priority_set.c"

uint32_t open_cfw_cmsis_irq_context(void){return host_irq;}
#include "../../components/apollo_main/core_overlay/runtime_cmsis_thread_set_priority.c"

static void init_list(struct open_cfw_freertos_queue_next_list *list)
{memset(list,0,sizeof(*list));list->index=(struct open_cfw_freertos_queue_next_list_item *)&list->end;list->end.next=(void *)&list->end;list->end.previous=(void *)&list->end;}
void open_cfw_priority_host_reset(uint32_t current_priority,uint32_t other_priority,uint32_t other_base,uint32_t other_ready)
{
 memset(&host_current,0,sizeof(host_current));memset(&host_other,0,sizeof(host_other));
 for(unsigned i=0;i<56;i++)init_list(&host_ready[i]);
 host_current.priority=host_current.base_priority=current_priority;host_other.priority=other_priority;host_other.base_priority=other_base;
 host_current.event_list_item.item_value=56-current_priority;host_other.event_list_item.item_value=56-other_priority;
 if(other_ready){host_other.state_list_item.container=&host_ready[other_priority];host_ready[other_priority].item_count=1;}
 host_top=current_priority;host_enter=host_exit=host_yield=host_remove=host_irq=0;
}
int32_t open_cfw_priority_host_call(uint32_t use_current,int32_t priority)
{return open_cfw_cmsis_thread_set_priority(use_current?(void *)&host_current:(void *)&host_other,priority);}
void open_cfw_priority_host_set_irq(uint32_t value){host_irq=value;}
uintptr_t open_cfw_priority_host_get(uint32_t selector)
{
 switch(selector){case 0:return host_other.priority;case 1:return host_other.base_priority;case 2:return host_other.event_list_item.item_value;case 3:return host_other.state_list_item.container==&host_ready[host_other.priority];case 4:return host_top;case 5:return host_yield;case 6:return host_remove;case 7:return host_enter;case 8:return host_exit;case 9:return host_current.priority;case 10:return host_current.base_priority;default:return 0;}
}
