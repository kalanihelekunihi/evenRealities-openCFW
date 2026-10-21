#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Only the authenticated 16-byte task-context prefix is owned here. Task
 * creators/stoppers and all later task-private fields remain separate gates. */
struct r1_event_context {
    void (*create)(void), (*stop)(void);
    void *thread, *queue;
};
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

/* 0x8d8fc. The stock leading record word is never initialized here. Do not
 * silently synthesize an owner/context value; its downstream meaning is open. */
uint32_t r1_event_publish(uint32_t id,const void *payload,uint32_t length)
{
    struct r1_event_context *context;
    if (id-1u<0xfffu) context=&r1_event_sensor;
    else if (id-0xfffu<=0x1000u) context=&r1_event_system;
    else if (id-0x1fffu<=0x1000u) context=&r1_event_storage;
    else return 0;
    struct { uint32_t unspecified,id,length; union { uint32_t word; void *pointer; } payload; } record;
    record.id=id;record.length=length;
    if (length<=4) {
        record.payload.word=0;
        memcpy(&record.payload.word,payload,length);
    } else {
        void *copy=pvPortMalloc(length);
        if (!copy) {
            if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
                r1_structured_log_format(0x04800000,"[RING]malloc fail, id:%d, msg_len:%d","[RING]malloc fail, id:%d, msg_len:%d",id,length);
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_2(0x1c0001,"malloc fail, id:%d, msg_len:%d",id,length);
            return 0;
        }
        memcpy(copy,payload,length);record.payload.pointer=copy;
    }
    if (r1_event_bus_enqueue(context,&record)) return 1;
    if (length>4) vPortFree(record.payload.pointer);
    return 0;
}
