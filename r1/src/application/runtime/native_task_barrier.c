/* Stock 0x46dcc: ordered suspension requests over existing live owners. */
#include "native_task_suspend.h"
#include "../board/native_task_contexts.h"
extern void *volatile r1_battery_thread_handle,*volatile r1_bae8_rx_thread;
extern void *volatile r1_factory_rx_thread,*volatile r1_touch_task_thread_handle;
extern void *volatile r1_protocol_service_thread;
extern uint32_t r1_advertising_configuration_byte_get(void);
void r1_task_suspend_barrier(void)
{
 r1_task_suspend_handshake(((volatile struct r1_event_context *)&r1_event_storage)->thread,0);
 r1_task_suspend_handshake(r1_battery_thread_handle,1);
 r1_task_suspend_handshake(r1_bae8_rx_thread,2);
 r1_task_suspend_handshake(((volatile struct r1_tx_context *)&r1_tx_channel1)->thread,3);
 r1_task_suspend_handshake(((volatile struct r1_tx_context *)&r1_tx_shared)->thread,10);
 r1_task_suspend_handshake(((volatile struct r1_event_context *)&r1_event_sensor)->thread,7);
 if (r1_advertising_configuration_byte_get()==0x55)
  r1_task_suspend_handshake(r1_factory_rx_thread,6);
 else
  r1_task_suspend_handshake(((volatile struct r1_event_context *)&r1_event_system)->thread,5);
 r1_task_suspend_handshake(r1_touch_task_thread_handle,9);
 r1_task_suspend_handshake(r1_protocol_service_thread,4);
}
