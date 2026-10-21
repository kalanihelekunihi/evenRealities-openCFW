/* R1 product-owned configuration recovered from authenticated native bodies.
 * Persistent storage and the status-ring publisher remain explicit providers. */
#include <stdint.h>
#include <string.h>
#define SVCALL_AS_NORMAL_FUNCTION
#include "ble_advertising.h"
extern void *volatile r1_device_info_kv_handle;
extern uint32_t r1_kv_class_read(void *,void *,uint32_t);
extern void r1_adc_error(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void r1_status_record_ring_publish(uint32_t,uint32_t,uint32_t,uint32_t);
extern ble_advertising_t r1_ble_advertising_context_a;
uint8_t r1_advertising_product_payload[21] __attribute__((section(".r1.advertising.product_payload")));
const ble_advdata_conn_int_t r1_advertising_connection_intervals __attribute__((section(".r1.advertising.intervals")))={24,40};
#define TEXT(name,value) const char r1_advertising_##name[] __attribute__((section(".r1.advertising.log." #name),aligned(1)))=value
TEXT(fast_ring,"[RING]Fast advertising.");TEXT(fast_sdk,"Fast advertising.");
TEXT(slow_ring,"[RING]Slow advertising.");TEXT(slow_sdk,"Slow advertising.");
uint32_t r1_advertising_configuration_byte_get(void)
{
    uint8_t record[124];
    (void)r1_kv_class_read(r1_device_info_kv_handle,record,sizeof(record));
    return record[112];
}
void r1_advertising_product_sn_read(uint8_t *destination,uint8_t *length)
{
    uint8_t record[124];
    (void)r1_kv_class_read(r1_device_info_kv_handle,record,sizeof(record));
    if (record[61]!=255) { memcpy(destination,record+31,15);if (length) *length=15; }
    else { memset(destination,255,15);if (length) *length=0; }
}
void r1_advertising_params_init(ble_adv_modes_config_t *config)
{
    memset(config,0,sizeof(*config));
    config->ble_adv_fast_enabled=true;config->ble_adv_fast_interval=160;
    config->ble_adv_fast_timeout=r1_advertising_configuration_byte_get()==85 ? 0:6000;
    config->ble_adv_slow_enabled=r1_advertising_configuration_byte_get()!=85;
    config->ble_adv_slow_interval=1600;config->ble_adv_slow_timeout=0;
}
void r1_advertising_status_publish(uint32_t enabled,uint32_t event)
{ r1_status_record_ring_publish(1,event,enabled ? 2:3,0); }
void r1_advertising_event_plan_build(ble_adv_evt_t event)
{
    if (event==BLE_ADV_EVT_IDLE) { r1_advertising_status_publish(0,0);return; }
    if (event!=BLE_ADV_EVT_FAST && event!=BLE_ADV_EVT_SLOW) return;
    const char *ring=event==BLE_ADV_EVT_FAST ? r1_advertising_fast_ring:r1_advertising_slow_ring;
    const char *sdk=event==BLE_ADV_EVT_FAST ? r1_advertising_fast_sdk:r1_advertising_slow_sdk;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x0c000000,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0003,sdk);
    r1_advertising_status_publish(1,event==BLE_ADV_EVT_FAST ? 1:2);
}
__attribute__((naked)) uint32_t r1_advertising_controller_address_get(ble_gap_addr_t *address __attribute__((unused)))
{ __asm__ volatile("svc %0\nbx lr"::"I"(SD_BLE_GAP_ADDR_GET):"r0","memory"); }
void r1_nordic_advertising_configuration(void)
{
    ble_advertising_init_t init;memset(&init,0,sizeof(init));
    init.advdata.name_type=BLE_ADVDATA_FULL_NAME;init.advdata.include_appearance=true;init.advdata.flags=6;
    ble_advdata_conn_int_t intervals=r1_advertising_connection_intervals;
    init.srdata.p_slave_conn_int=&intervals;
    ble_gap_addr_t address;
    uint32_t status=r1_advertising_controller_address_get(&address);
    if (status) r1_adc_error(status);
    memcpy(r1_advertising_product_payload,address.addr,6);
    uint8_t serial_length=0;r1_advertising_product_sn_read(r1_advertising_product_payload+6,&serial_length);
    ble_advdata_manuf_data_t manufacturer={.company_identifier=0x5245,.data={.size=serial_length>=15 ? 21:6,.p_data=r1_advertising_product_payload}};
    init.srdata.p_manuf_specific_data=&manufacturer;
    r1_advertising_params_init(&init.config);init.evt_handler=r1_advertising_event_plan_build;
    status=ble_advertising_init(&r1_ble_advertising_context_a,&init);
    if (status) r1_adc_error(status);
    ble_advertising_conn_cfg_tag_set(&r1_ble_advertising_context_a,1);
}
