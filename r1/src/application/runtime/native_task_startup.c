/* Stock 0x46b20: construct workers through live lifecycle prefix callbacks. */
#include "cmsis_os2.h"
#include "../board/native_task_contexts.h"
extern void r1_native_delayed_initialize(void);
extern uint32_t r1_native_watchdog_initialize(void),r1_advertising_configuration_byte_get(void);
void r1_task_startup(void)
{
 r1_native_delayed_initialize();
 (void)r1_native_watchdog_initialize();
 ((volatile struct r1_event_context *)&r1_event_storage)->create();
 (void)osThreadSetPriority(osThreadGetId(),(osPriority_t)8);
 ((volatile struct r1_nfc_charge_lifecycle *)&r1_nfc_charge_lifecycle)->create();
 ((volatile struct r1_bae8_rx_lifecycle *)&r1_bae8_rx_lifecycle)->create();
 ((volatile struct r1_tx_context *)&r1_tx_channel1)->create();
 ((volatile struct r1_tx_context *)&r1_tx_shared)->create();
 ((volatile struct r1_task_lifecycle *)&r1_ble_io_lifecycle)->create();
 ((volatile struct r1_event_context *)&r1_event_sensor)->create();
 if (r1_advertising_configuration_byte_get()==0x55)
  ((volatile struct r1_factory_lifecycle *)&r1_factory_rx_lifecycle)->create();
 else
  ((volatile struct r1_event_context *)&r1_event_system)->create();
 ((volatile struct r1_task_lifecycle *)&r1_touch_io_lifecycle)->create();
 (void)osThreadSetPriority(osThreadGetId(),(osPriority_t)53);
}
