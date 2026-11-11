#include <stdint.h>
#include <stddef.h>
#include "native_task_contexts.h"

/* Only the authenticated 16-byte task-context prefix is owned here. Task
 * creators/stoppers and all later task-private fields remain separate gates. */
extern void r1_thread_create_a(void),r1_task_stop_668c(void);
extern void r1_thread_create_f(void),r1_task_stop_6608(void);
extern void r1_thread_create_g(void),r1_task_stop_66d8(void);
struct r1_event_context r1_event_sensor
 __attribute__((section(".r1.event.sensor"),aligned(4)))={r1_thread_create_a,r1_task_stop_668c,0,0};
struct r1_event_context r1_event_system
 __attribute__((section(".r1.event.system"),aligned(4)))={r1_thread_create_f,r1_task_stop_6608,0,0};
struct r1_event_context r1_event_storage
 __attribute__((section(".r1.event.storage"),aligned(4)))={r1_thread_create_g,r1_task_stop_66d8,0,0};

extern int32_t osMessageQueuePut(void *,const void *,uint8_t,uint32_t);
extern uint32_t osThreadFlagsSet(void *,uint32_t);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern void *r1_native_memory_move(void *,const void *,size_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);

/* 0x924c0: a failed send still wakes the consumer. */
uint32_t r1_event_bus_enqueue(struct r1_event_context *context,const void *record)
{
    if (!context || !context->thread || !record || !context->queue) return 0;
    int32_t status=osMessageQueuePut(context->queue,record,0,0);
    osThreadFlagsSet(context->thread,0x400000);
    return status==0;
}

/* Native frame bytes are supplied by the bridge, including the existing
 * leading queue-record word at frame+4. No indeterminate C local is used. */
__attribute__((used,noinline)) static uint32_t event_publish_body(
 uint32_t id,const void *payload,uint32_t length,volatile uint32_t *frame)
{
    struct r1_event_context *context;
    if (id-1u<0xfffu) context=&r1_event_sensor;
    else if (id-0xfffu<=0x1000u) context=&r1_event_system;
    else if (id-0x1fffu<=0x1000u) context=&r1_event_storage;
    else return 0;
    frame[2]=id;frame[3]=length;
    if (length<=4) {
        frame[4]=0;
        r1_native_memory_move((void *)(uintptr_t)(frame+4),payload,length);
    } else {
        void *copy=pvPortMalloc(length);
        if (!copy) {
            if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
                frame[0]=length;
                r1_structured_log_format(0x04800000,"[RING]malloc fail, id:%d, msg_len:%d","[RING]malloc fail, id:%d, msg_len:%d",id,length);
            }
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_2(0x1c0001,"malloc fail, id:%d, msg_len:%d",id,length);
            return 0;
        }
        r1_native_memory_move(copy,payload,length);frame[4]=(uint32_t)(uintptr_t)copy;
    }
    if (r1_event_bus_enqueue(context,(const void *)(uintptr_t)(frame+1))) return 1;
    if (length>4) vPortFree((void *)(uintptr_t)frame[4]);
    return 0;
}

/* The queue consumer reads the ID, length and payload fields at words 1..3 of
 * the submitted record. Its leading word is padding, so define it in C. */
uint32_t r1_event_publish(uint32_t id,const void *payload,uint32_t length)
{
 volatile uint32_t frame[5]={0};
 return event_publish_body(id,payload,length,frame);
}
