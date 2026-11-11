/* Stock late NFC/charger setup and IRQ adapters. The legacy PMIC names are
 * retained; GPO binding uses the existing I2C5 resource owner. */
#include <stdint.h>
#include "../i2c5/stock_transport.h"
#include "../registry/stock_registry.h"
extern void r1_i2c5_nfc_resource_acquire(void),r1_i2c5_nfc_resource_release(void);
extern void nrf_delay_ms(uint32_t);
extern void r1_st25dvxxkc_initialize_configuration(void);
extern uint32_t r1_yhm_transport_release(void),r1_yhm_irq_register(uint32_t);
extern uint32_t r1_yhm_block_word_set(uint32_t);
extern uint32_t r1_battery_task_flags_set(uint32_t);
extern uint32_t r1_advertising_configuration_byte_get(void);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern void r1_nfc_charge_monitor_callback_00042d40(uint32_t);
volatile uint8_t r1_nfc_charge_late_flag
 __attribute__((section(".r1.nfc.charge.late_flag")))=0;
static generic_device_registry_device *gpo(void)
{
 return ((volatile r1_i2c5_stock_state *)&r1_i2c5_state)->gpo;
}
uint32_t r1_nfc_gpo_release(void)
{
 return r1_stock_dispatch_0c(gpo());
}
uint32_t r1_pmic_event_op_dispatch(uint32_t callback)
{
 (void)r1_stock_dispatch_08(gpo());
 /* Opening can replace the cached input device. Read the owner again. */
 return r1_stock_dispatch_20(gpo(),0,callback);
}
uint32_t r1_pmic_post_device_callback_plan(uint32_t argument)
{
 (void)argument;
 (void)r1_nfc_gpo_release();
 return r1_battery_task_flags_set(1);
}
uint32_t r1_charge_event_i2c_op(uint32_t argument)
{
 (void)argument;
 (void)r1_yhm_transport_release();
 return r1_yhm_irq_register((uint32_t)(uintptr_t)r1_nfc_charge_monitor_callback_00042d40);
}
void r1_pmic_charge_i2c_callback_plan(uint32_t argument)
{
 (void)argument;
 (void)r1_yhm_transport_release();
 (void)r1_battery_task_flags_set(2);
}
void r1_pmic_late_init_plan_build(void)
{
 r1_nfc_charge_late_flag=0;
 r1_i2c5_nfc_resource_acquire();
 nrf_delay_ms(50);
 (void)r1_st25dvxxkc_initialize_configuration();
 r1_i2c5_nfc_resource_release();
 (void)r1_charge_event_i2c_op(0);
 (void)r1_yhm_block_word_set((uint32_t)(uintptr_t)r1_charge_event_i2c_op);
 (void)r1_pmic_event_op_dispatch((uint32_t)(uintptr_t)r1_pmic_post_device_callback_plan);
 if(r1_advertising_configuration_byte_get()==0x55)
  r1_native_delayed_schedule(r1_pmic_charge_i2c_callback_plan,0,0x400);
}
