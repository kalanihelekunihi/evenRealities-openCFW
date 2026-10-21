#include <stdint.h>
extern int32_t osMessageQueuePut(void *,const void *,uint8_t,uint32_t);
extern uint32_t osThreadFlagsSet(void *,uint32_t);
extern void *volatile r1_touch_task_thread_handle;
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_0(uint32_t,const char *);
/* Shared native task-context field at20006664+12. The diagnostic label names
 * NFC/charge; no claim that this queue is exclusively a touch task is implied. */
void *volatile r1_touch_task_message_queue __attribute__((section(".r1.touch.task.queue"),aligned(4)))=0;
const char r1_touch_task_queue_null_ring[] __attribute__((section(".r1.touch.task.null_ring")))="[RING]nfc_charge_task_msg_send queue null";
const char r1_touch_task_queue_null_sdk[] __attribute__((section(".r1.touch.task.null_sdk")))="nfc_charge_task_msg_send queue null";
const char r1_touch_task_missed_ring[] __attribute__((section(".r1.touch.task.missed_ring")))="[RING]msg missed";
const char r1_touch_task_missed_sdk[] __attribute__((section(".r1.touch.task.missed_sdk")))="msg missed";
static void queue_error(const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x04000000,ring,ring);
 if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_0(0x001c0001,sdk);
}
uint32_t r1_touch_task_message_boundary(const void *message)
{
 void *queue=r1_touch_task_message_queue;
 if(!queue){queue_error(r1_touch_task_queue_null_ring,r1_touch_task_queue_null_sdk);return 0;}
 if(osMessageQueuePut(queue,message,0,0)){
  queue_error(r1_touch_task_missed_ring,r1_touch_task_missed_sdk);return 0;
 }
 (void)osThreadFlagsSet(r1_touch_task_thread_handle,0x400000);
 return 1;
}
