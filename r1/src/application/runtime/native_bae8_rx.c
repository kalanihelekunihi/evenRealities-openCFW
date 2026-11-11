/* Stock R1 0x33dbc. This RX queue at 0x2000659c is distinct from the
 * existing BLE event-message queue at 0x20006574. Ownership transfers only
 * after a successful queue put; the explicit C frame preserves its input slot. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
extern void *pvPortMalloc(uint32_t);
extern void vPortFree(void *);
extern void *r1_native_memory_move(void *,const void *,size_t);
extern uint32_t osMessageQueueGetCount(void *),osMessageQueueGetCapacity(void *);
extern int32_t osMessageQueuePut(void *,const void *,uint8_t,uint32_t);
extern uint32_t osThreadFlagsSet(void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
void *volatile r1_bae8_rx_thread __attribute__((section(".r1.bae8.rx.thread"),aligned(4)));
void *volatile r1_bae8_rx_queue __attribute__((section(".r1.bae8.rx.queue"),aligned(4)));
struct message {uint32_t handle,channel,length;uint8_t payload[];};
_Static_assert(sizeof(struct message)==12,"native receive header");
static const char null_ring[]="[RING]ble msg msg buffer is null";
static const char null_sdk[]="ble msg msg buffer is null";
static const char queue_ring[]="[RING]Thread_MsgRxFromBle queue null";
static const char queue_sdk[]="Thread_MsgRxFromBle queue null";
static const char alloc_ring[]="[RING]Thread_MsgRxFromBle alloc length = %d fail";
static const char alloc_sdk[]="Thread_MsgRxFromBle alloc length = %d fail";
static const char put_ring[]="[RING]ble msg send msg fail, status = %d";
static const char put_sdk[]="ble msg send msg fail, status = %d";
struct rx_frame {struct message *volatile message;uint32_t private_padding[7];};
_Static_assert(sizeof(struct rx_frame)==32,"C receive frame");
_Static_assert(offsetof(struct rx_frame,message)==0,"stock pointer slot");
uint32_t r1_bae8_bc_rx_enqueue(uint32_t handle,uint32_t channel,const void *payload,uint32_t length)
{
    _Alignas(8) struct rx_frame frame;
    const char *ring,*sdk;
    if (!payload) {ring=null_ring;sdk=null_sdk;goto plain_failure;}
    if (!r1_bae8_rx_queue) {ring=queue_ring;sdk=queue_sdk;goto plain_failure;}
    frame.message=0;
    frame.message=pvPortMalloc((length+15u)&~3u);
    if (!frame.message) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04400000,alloc_ring,alloc_ring,length);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0001,alloc_sdk,length);
        return UINT32_MAX;
    }
    memset(frame.message->payload,0,length);
    frame.message->handle=handle;frame.message->channel=channel;frame.message->length=length;
    r1_native_memory_move(frame.message->payload,payload,length);
    (void)osMessageQueueGetCount(r1_bae8_rx_queue);
    (void)osMessageQueueGetCapacity(r1_bae8_rx_queue);
    int32_t status=osMessageQueuePut(r1_bae8_rx_queue,(const void *)&frame.message,0,0);
    if (status) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04400000,put_ring,put_ring,(uint32_t)status);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0001,put_sdk,(uint32_t)status);
        vPortFree(frame.message);frame.message=0;return UINT32_MAX;
    }
    (void)osThreadFlagsSet(r1_bae8_rx_thread,0x400000);
    return 0;
plain_failure:
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0001,sdk);
    return UINT32_MAX;
}
