/* Stock R1 RX drain 0x450cc and stop 0x4503c. The pointer slot is borrowed
 * by QueueGet; callbacks can change it and the message before later reloads. */
#include <stdint.h>
#include <stddef.h>
extern void *volatile r1_bae8_rx_thread,*volatile r1_bae8_rx_queue;
extern int32_t osMessageQueueGet(void *,void *,uint8_t *,uint32_t);
extern int32_t osThreadTerminate(void *);
extern uint32_t r1_conn_field6_set(uint32_t);
extern void r1_native_watchdog_arm(uint32_t),r1_native_watchdog_disarm(uint32_t);
extern void r1_export_plan_command(uint32_t,void *,uint32_t);
extern uint32_t r1_proto_ble_recv_validate(uint32_t,const void *,uint32_t);
extern uint32_t r1_legacy_command_route_frame(uint32_t,const void *,uint32_t);
extern void r1_eat_command_tokenize(void *);
extern void vPortFree(void *);
uint32_t volatile r1_bae8_rx_watchdog __attribute__((section(".r1.bae8.rx.watchdog"),aligned(4)));
struct rx_message {uint32_t handle,channel,length;uint8_t payload[];};
void r1_task_stop_6590(void)
{
    void *thread=r1_bae8_rx_thread;
    if (thread) { (void)osThreadTerminate(thread);r1_bae8_rx_thread=0; }
}
void r1_message_pump_task(void)
{
    struct rx_message *message=0;
    while (osMessageQueueGet(r1_bae8_rx_queue,(void *)&message,0,0)==0) {
        if (!message) continue;
        if (message->handle!=UINT32_C(0xffff)) (void)r1_conn_field6_set((uint16_t)message->handle);
        if (message->channel==2) {
            if (message->payload[0]<100) {
                r1_native_watchdog_arm(r1_bae8_rx_watchdog);
                r1_export_plan_command((uint16_t)message->handle,message->payload,(uint16_t)message->length);
                r1_native_watchdog_disarm(r1_bae8_rx_watchdog);
            } else {
                (void)r1_proto_ble_recv_validate(message->handle,message->payload,(uint16_t)message->length);
            }
        } else if (message->channel==1) {
            uint32_t length=message->length;
            if (length>3 && message->payload[0]=='A' && message->payload[1]=='T' && message->payload[2]=='^') {
                *(uint8_t *)((uintptr_t)message+12u+length)=0;
                r1_eat_command_tokenize(message->payload);
            } else {
                (void)r1_legacy_command_route_frame((uint16_t)message->handle,message->payload,(uint16_t)length);
            }
        }
        vPortFree(message);message=0;
    }
}
