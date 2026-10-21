#include <stdint.h>
#include <stddef.h>
#include <string.h>

struct r1_tx_context { void (*create)(void),(*stop)(void); void *thread,*queue; };
extern void r1_thread_create_e(void),r1_task_stop_65bc(void);
extern void r1_thread_create_b(void),r1_task_stop_65e0(void);
struct r1_tx_context r1_tx_channel1
 __attribute__((section(".r1.tx.channel1"),aligned(4)))={r1_thread_create_e,r1_task_stop_65bc,0,0};
struct r1_tx_context r1_tx_shared
 __attribute__((section(".r1.tx.shared"),aligned(4)))={r1_thread_create_b,r1_task_stop_65e0,0,0};
extern uint32_t r1_glasses_connection_handle_get(void),r1_phone_connection_handle_get(void);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern uint32_t osMessageQueueGetCount(void *),osMessageQueueGetCapacity(void *);
extern int32_t osMessageQueuePut(void *,const void *,uint8_t,uint32_t);
extern uint32_t osThreadFlagsSet(void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);

static void log_error(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x1c0001,sdk);
}

/* Shared stock body 0x3e274, reached by the three 12-byte native veneers.
 * Preserve unsigned overflow, diagnostic-only fullness warnings and ownership
 * transfer of heap envelopes. Real allocator/queue workers remain providers. */
static int32_t dispatch(uint32_t type,uint32_t id,const void *payload,uint32_t length)
{
    if (!payload) {
        log_error("[RING]msg dispatch msg buffer is null","msg dispatch msg buffer is null");
        return -1;
    }
    struct r1_tx_context *context=type==0 ? &r1_tx_shared : &r1_tx_channel1;
    if (!context->queue) {
        log_error("[RING]ble tx queue null","ble tx queue null");return -1;
    }
    if (type==0 && r1_glasses_connection_handle_get()==0xffff) {
        log_error("[RING]glasses conn handle is invalid","glasses conn handle is invalid");return -1;
    }
    if (type==1 && r1_phone_connection_handle_get()==0xffff) {
        log_error("[RING]phone conn handle is invalid","phone conn handle is invalid");return -1;
    }
    uint32_t *envelope=pvPortMalloc((length+15u)&~UINT32_C(3));
    if (!envelope) {
        log_error("[RING]_dispatchMsgTxByBle alloc fail","_dispatchMsgTxByBle alloc fail");return -1;
    }
    envelope[0]=id;envelope[1]=type;envelope[2]=length;
    memcpy(envelope+3,payload,length);
    uint32_t count=osMessageQueueGetCount(context->queue);
    uint32_t capacity=osMessageQueueGetCapacity(context->queue);
    if (capacity*9u<=count*10u) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x08800000,"[RING]Queue nearly full: %d/%d, drop message","[RING]Queue nearly full: %d/%d, drop message",count,capacity);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_2(0x1c0002,"Queue nearly full: %d/%d, drop message",count,capacity);
    }
    int32_t status=osMessageQueuePut(context->queue,&envelope,0,100);
    if (status==0) { osThreadFlagsSet(context->thread,1);return 0; }
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04c00000,"[RING]msg ble tx dispatch send msg, status = %d, queue: %d/%d","[RING]msg ble tx dispatch send msg, status = %d, queue: %d/%d",(uint32_t)status,count,capacity);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_3(0x1c0001,"msg ble tx dispatch send msg, status = %d, queue: %d/%d",(uint32_t)status,count,capacity);
    vPortFree(envelope);return -1;
}
int32_t r1_ble_tx_queue_dispatch_type0(uint32_t id,const void *payload,uint32_t length)
{ return dispatch(0,id,payload,length); }
int32_t r1_ble_tx_queue_dispatch_type1(uint32_t id,const void *payload,uint32_t length)
{ return dispatch(1,id,payload,length); }
int32_t r1_ble_tx_queue_dispatch_type2(uint32_t id,const void *payload,uint32_t length)
{ return dispatch(2,id,payload,length); }
