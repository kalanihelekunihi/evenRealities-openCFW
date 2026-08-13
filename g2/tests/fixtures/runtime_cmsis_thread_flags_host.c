#include <stddef.h>
#include <stdint.h>
#include <string.h>

struct open_cfw_freertos_notify_tcb;
static struct open_cfw_freertos_notify_tcb *host_current_ptr;
static uint32_t host_top_ready,host_suspended,host_yield_pending,host_tick;
static uint32_t host_irq,host_mask,host_yield_mode,host_yield_value,host_pendsv;
static size_t host_enter,host_exit,host_yield,host_delay,host_remove;
static size_t host_insert_ready,host_insert_pending,host_validate,host_assert;

#define OPEN_CFW_FREERTOS_NOTIFY_CURRENT_TCB_LOAD() (host_current_ptr)
#define OPEN_CFW_FREERTOS_NOTIFY_READY_LIST(priority) (&host_ready[(priority)])
#define OPEN_CFW_FREERTOS_NOTIFY_TOP_READY_LOAD() (host_top_ready)
#define OPEN_CFW_FREERTOS_NOTIFY_TOP_READY_STORE(value) (host_top_ready=(value))
#define OPEN_CFW_FREERTOS_NOTIFY_SCHEDULER_SUSPENDED_LOAD() (host_suspended)
#define OPEN_CFW_FREERTOS_NOTIFY_PENDING_READY_LIST() (&host_pending)
#define OPEN_CFW_FREERTOS_NOTIFY_YIELD_PENDING_STORE(value) (host_yield_pending=(value))
#define OPEN_CFW_FREERTOS_NOTIFY_TICK_COUNT_LOAD() (host_tick)
#define OPEN_CFW_FREERTOS_NOTIFY_SET_MASK() (++host_mask,0x51U)
#define OPEN_CFW_FREERTOS_NOTIFY_CLEAR_MASK(mask) do {host_mask=(mask);} while(0)
#define OPEN_CFW_FREERTOS_NOTIFY_VALIDATE_INTERRUPT_PRIORITY() (++host_validate)
#define OPEN_CFW_FREERTOS_NOTIFY_ASSERT(condition) do {if(!(condition))++host_assert;} while(0)

#include "../../components/shared/freertos/runtime_freertos_task_notify.h"

static struct open_cfw_freertos_notify_tcb host_current,host_target;
static struct open_cfw_freertos_queue_next_list host_ready[56],host_pending;

void open_cfw_freertos_port_enter_critical(void){++host_enter;}
void open_cfw_freertos_port_exit_critical(void){++host_exit;}
void open_cfw_freertos_port_yield(void){
    ++host_yield;
    if(host_yield_mode!=0U){host_current.notification_value=host_yield_value;host_current.notification_state=OPEN_CFW_FREERTOS_NOTIFY_RECEIVED;}
}
open_cfw_freertos_queue_next_ubase_type open_cfw_freertos_list_remove(
    struct open_cfw_freertos_queue_next_list_item *item
){++host_remove;item->container=0;return 0;}
void open_cfw_freertos_list_insert_end(
    struct open_cfw_freertos_queue_next_list *list,
    struct open_cfw_freertos_queue_next_list_item *item
){
    item->container=list;++list->item_count;
    if(list==&host_pending)++host_insert_pending;else ++host_insert_ready;
}
void open_cfw_freertos_task_reset_next_task_unblock_time(void){++host_delay;}
void open_cfw_freertos_task_add_current_to_delayed_list(
    open_cfw_freertos_queue_next_tick_type ticks,
    open_cfw_freertos_queue_next_base_type indefinite
){(void)ticks;(void)indefinite;++host_delay;}

#include "../../components/shared/freertos/runtime_freertos_task_notify.c"

#define OPEN_CFW_CMSIS_THREAD_FLAGS_PENDSV() (++host_pendsv)
#include "../../components/apollo_main/core_overlay/runtime_cmsis_thread_flags.c"

uint32_t open_cfw_cmsis_irq_context(void){return host_irq;}
uint32_t open_cfw_freertos_task_get_tick_count(void){return host_tick++;}

void open_cfw_thread_flags_host_reset(uint32_t current_priority,uint32_t target_priority){
 memset(&host_current,0,sizeof(host_current));memset(&host_target,0,sizeof(host_target));
 memset(host_ready,0,sizeof(host_ready));memset(&host_pending,0,sizeof(host_pending));
 host_current.priority=current_priority;host_target.priority=target_priority;
 host_current_ptr=&host_current;host_top_ready=0;host_suspended=0;host_yield_pending=0;
 host_tick=0;host_irq=0;host_mask=0;host_yield_mode=0;host_yield_value=0;host_pendsv=0;
 host_enter=host_exit=host_yield=host_delay=host_remove=0;
 host_insert_ready=host_insert_pending=host_validate=host_assert=0;
}
void open_cfw_thread_flags_host_set_target(uint32_t value,uint32_t state,uint32_t blocked){
 host_target.notification_value=value;host_target.notification_state=(unsigned char)state;
 host_target.state_list_item.container=blocked?&host_ready[0]:0;host_target.event_list_item.container=0;
}
void open_cfw_thread_flags_host_set_current(uint32_t value,uint32_t state){host_current.notification_value=value;host_current.notification_state=(unsigned char)state;}
void open_cfw_thread_flags_host_set_irq(uint32_t value){host_irq=value;}
void open_cfw_thread_flags_host_set_suspended(uint32_t value){host_suspended=value;}
void open_cfw_thread_flags_host_set_tick(uint32_t value){host_tick=value;}
void open_cfw_thread_flags_host_set_yield_notification(uint32_t enabled,uint32_t value){host_yield_mode=enabled;host_yield_value=value;}
int32_t open_cfw_thread_flags_host_notify(uint32_t value,uint32_t action,uint32_t from_isr,uint32_t query,uint32_t *previous,uint32_t *woken){
 if(from_isr)return open_cfw_freertos_task_notify_from_isr(&host_target,0,value,(open_cfw_freertos_queue_next_base_type)action,query?previous:0,(open_cfw_freertos_queue_next_base_type *)woken);
 return open_cfw_freertos_task_notify(&host_target,0,value,(open_cfw_freertos_queue_next_base_type)action,query?previous:0);
}
int32_t open_cfw_thread_flags_host_wait_kernel(uint32_t clear_entry,uint32_t clear_exit,uint32_t timeout,uint32_t *value){return open_cfw_freertos_task_notify_wait(0,clear_entry,clear_exit,value,timeout);}
uint32_t open_cfw_thread_flags_host_set_wrapper(uint32_t null_task,uint32_t flags){return open_cfw_cmsis_thread_flags_set(null_task?0:&host_target,flags);}
uint32_t open_cfw_thread_flags_host_wait_wrapper(uint32_t flags,uint32_t options,uint32_t timeout){return open_cfw_cmsis_thread_flags_wait(flags,options,timeout);}
size_t open_cfw_thread_flags_host_get(uint32_t index){
 size_t values[]={host_target.notification_value,host_target.notification_state,host_current.notification_value,host_current.notification_state,host_enter,host_exit,host_yield,host_delay,host_remove,host_insert_ready,host_insert_pending,host_top_ready,host_yield_pending,host_mask,host_validate,host_assert,host_pendsv,host_tick};
 return index<sizeof(values)/sizeof(values[0])?values[index]:0;
}
