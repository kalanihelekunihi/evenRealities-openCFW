#include <stdint.h>
extern void *pvPortMalloc(uint32_t);
extern void vPortFree(void *);
extern void r1_native_memory_move(void *,const void *,uint32_t);
extern int32_t osMessageQueuePut(void *,const void *,uint8_t,uint32_t);
extern uint32_t osThreadFlagsSet(void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_0(uint32_t,const char *);
extern void *volatile r1_protocol_service_thread;
void *volatile r1_ble_message_queue __attribute__((section(".r1.ble.message.queue"),aligned(4)))=0;
const char r1_ble_message_log0[] __attribute__((section(".r1.ble.message.log0")))="[RING]Thread_BleEventMsgSend pdata is null";
const char r1_ble_message_log1[] __attribute__((section(".r1.ble.message.log1")))="Thread_BleEventMsgSend pdata is null";
const char r1_ble_message_log2[] __attribute__((section(".r1.ble.message.log2")))="[RING]g_thread_ble.h_message_queue queue null";
const char r1_ble_message_log3[] __attribute__((section(".r1.ble.message.log3")))="g_thread_ble.h_message_queue queue null";
const char r1_ble_message_log4[] __attribute__((section(".r1.ble.message.log4")))="[RING]Thread_BleEventMsgSend alloc fail";
const char r1_ble_message_log5[] __attribute__((section(".r1.ble.message.log5")))="Thread_BleEventMsgSend alloc fail";
const char r1_ble_message_log6[] __attribute__((section(".r1.ble.message.log6")))="[RING]Thread_BleEventMsgSend msg queue put fail";
const char r1_ble_message_log7[] __attribute__((section(".r1.ble.message.log7")))="Thread_BleEventMsgSend msg queue put fail";
static void error_log(const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x04000000,ring,ring);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_0(0x001c0001,sdk);
}
uint32_t r1_ble_thread_message_encode(uint32_t handle,uint32_t event,uint32_t length,const void *payload)
{
 if(length && !payload){error_log(r1_ble_message_log0,r1_ble_message_log1);return UINT32_MAX;}
 if(!r1_ble_message_queue){error_log(r1_ble_message_log2,r1_ble_message_log3);return UINT32_MAX;}
 uint32_t *message=pvPortMalloc((length+15u)&~3u);
 if(!message){error_log(r1_ble_message_log4,r1_ble_message_log5);return UINT32_MAX;}
 message[0]=handle;message[1]=event;message[2]=length;
 r1_native_memory_move(message+3,payload,length);
 if(osMessageQueuePut(r1_ble_message_queue,&message,0,0)){
  error_log(r1_ble_message_log6,r1_ble_message_log7);
  vPortFree(message);message=0;return UINT32_MAX;
 }
 (void)osThreadFlagsSet(r1_protocol_service_thread,0x400000);
 return 0;
}
