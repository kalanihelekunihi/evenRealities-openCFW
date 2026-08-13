#include <stddef.h>
#include <stdint.h>
#include <string.h>

static struct open_cfw_freertos_task_delete_tcb *host_current;
static struct open_cfw_freertos_queue_next_list *host_delayed_ptr;
static struct open_cfw_freertos_queue_next_list *host_overflow_ptr;
static uint32_t host_current_count,host_cleanup_count,host_task_number;
static int32_t host_scheduler_running;
static uint32_t host_scheduler_suspended,host_irq;
static size_t host_enter,host_exit,host_remove_state,host_remove_event;
static size_t host_insert,host_reset_unblock,host_free_stack,host_free_tcb;
static size_t host_yield,host_assert;

#define OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_TCB_LOAD() (host_current)
#define OPEN_CFW_FREERTOS_TASK_DELETE_DELAYED_LIST_LOAD() (host_delayed_ptr)
#define OPEN_CFW_FREERTOS_TASK_DELETE_OVERFLOW_LIST_LOAD() (host_overflow_ptr)
#define OPEN_CFW_FREERTOS_TASK_DELETE_TERMINATION_LIST() (&host_termination)
#define OPEN_CFW_FREERTOS_TASK_DELETE_SUSPENDED_LIST() (&host_suspended)
#define OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_COUNT() (host_current_count)
#define OPEN_CFW_FREERTOS_TASK_DELETE_CLEANUP_COUNT() (host_cleanup_count)
#define OPEN_CFW_FREERTOS_TASK_DELETE_TASK_NUMBER() (host_task_number)
#define OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_RUNNING_LOAD() (host_scheduler_running)
#define OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_SUSPENDED_LOAD() (host_scheduler_suspended)
#define OPEN_CFW_FREERTOS_TASK_DELETE_ASSERT(condition) do {if(!(condition))++host_assert;}while(0)

#include "../../components/shared/freertos/runtime_freertos_task_delete.h"

static struct open_cfw_freertos_task_delete_tcb host_target,host_other;
static struct open_cfw_freertos_queue_next_list host_ready,host_delayed;
static struct open_cfw_freertos_queue_next_list host_overflow,host_suspended;
static struct open_cfw_freertos_queue_next_list host_termination,host_event;

void open_cfw_freertos_port_enter_critical(void){++host_enter;}
void open_cfw_freertos_port_exit_critical(void){++host_exit;}
void open_cfw_freertos_port_yield(void){++host_yield;}
open_cfw_freertos_queue_next_ubase_type open_cfw_freertos_list_remove(struct open_cfw_freertos_queue_next_list_item *item){if(item==&host_target.state_list_item)++host_remove_state;else if(item==&host_target.event_list_item)++host_remove_event;item->container=0;return 0;}
void open_cfw_freertos_list_insert_end(struct open_cfw_freertos_queue_next_list *list,struct open_cfw_freertos_queue_next_list_item *item){++host_insert;item->container=list;}
void open_cfw_freertos_task_reset_next_task_unblock_time(void){++host_reset_unblock;}
void open_cfw_freertos_heap4_free(void *memory){if(memory==host_target.stack)++host_free_stack;else if(memory==&host_target)++host_free_tcb;}

#define OPEN_CFW_BUILD_TASK_GET_STATE
#include "../../components/shared/freertos/runtime_freertos_task_delete.c"
#undef OPEN_CFW_BUILD_TASK_GET_STATE
#define OPEN_CFW_BUILD_TASK_DELETE_TCB
#include "../../components/shared/freertos/runtime_freertos_task_delete.c"
#undef OPEN_CFW_BUILD_TASK_DELETE_TCB
#define OPEN_CFW_BUILD_TASK_DELETE
#include "../../components/shared/freertos/runtime_freertos_task_delete.c"
#undef OPEN_CFW_BUILD_TASK_DELETE

uint32_t open_cfw_cmsis_irq_context(void);
#define open_cfw_freertos_task_get_state open_cfw_freertos_task_get_state_cmsis
#include "../../components/apollo_main/core_overlay/runtime_cmsis_thread_terminate.c"
#undef open_cfw_freertos_task_get_state
uint32_t open_cfw_cmsis_irq_context(void){return host_irq;}
int open_cfw_freertos_task_get_state_cmsis(const struct open_cfw_freertos_task_delete_tcb *task){return (int)open_cfw_freertos_task_get_state(task);}

void open_cfw_terminate_host_reset(uint32_t mode,uint32_t is_current,uint32_t allocation,uint32_t scheduler_running){
 memset(&host_target,0,sizeof(host_target));memset(&host_other,0,sizeof(host_other));
 memset(&host_ready,0,sizeof(host_ready));memset(&host_delayed,0,sizeof(host_delayed));memset(&host_overflow,0,sizeof(host_overflow));memset(&host_suspended,0,sizeof(host_suspended));memset(&host_termination,0,sizeof(host_termination));memset(&host_event,0,sizeof(host_event));
 host_delayed_ptr=&host_delayed;host_overflow_ptr=&host_overflow;host_current=is_current?&host_target:&host_other;
 host_target.state_list_item.container=&host_ready;host_target.stack=(void *)(uintptr_t)0x12340000U;host_target.statically_allocated=(unsigned char)allocation;
 if(mode==1)host_target.state_list_item.container=&host_delayed;else if(mode==2)host_target.state_list_item.container=&host_overflow;else if(mode==3)host_target.state_list_item.container=&host_suspended;else if(mode==4){host_target.state_list_item.container=&host_suspended;host_target.event_list_item.container=&host_event;}else if(mode==5){host_target.state_list_item.container=&host_suspended;host_target.notify_state=1;}else if(mode==6)host_target.state_list_item.container=&host_termination;else if(mode==7)host_target.state_list_item.container=0;
 host_current_count=5;host_cleanup_count=1;host_task_number=9;host_scheduler_running=(int32_t)scheduler_running;host_scheduler_suspended=0;host_irq=0;host_enter=host_exit=host_remove_state=host_remove_event=host_insert=host_reset_unblock=host_free_stack=host_free_tcb=host_yield=host_assert=0;
}
int32_t open_cfw_terminate_host_state(void){return (int32_t)open_cfw_freertos_task_get_state(&host_target);}
void open_cfw_terminate_host_delete(uint32_t null_handle){open_cfw_freertos_task_delete(null_handle?0:&host_target);}
int32_t open_cfw_terminate_host_wrapper(uint32_t null_handle){return open_cfw_cmsis_thread_terminate(null_handle?0:&host_target);}
void open_cfw_terminate_host_set_irq(uint32_t value){host_irq=value;}
void open_cfw_terminate_host_set_suspended(uint32_t value){host_scheduler_suspended=value;}
size_t open_cfw_terminate_host_get(uint32_t index){size_t values[]={host_enter,host_exit,host_remove_state,host_remove_event,host_insert,host_reset_unblock,host_free_stack,host_free_tcb,host_yield,host_assert,host_current_count,host_cleanup_count,host_task_number,host_target.state_list_item.container==&host_termination};return index<sizeof(values)/sizeof(values[0])?values[index]:0;}
