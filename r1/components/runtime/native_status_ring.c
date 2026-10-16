#include <stdint.h>
/* Product status publisher0x5e118. Only authenticated cells are typed here;
 * ownership/initialization of the ring and device-state roots remains gated. */
volatile uint8_t r1_status_read_index __attribute__((section(".r1.status.read")))=0;
volatile uint8_t r1_status_write_index __attribute__((section(".r1.status.write")))=0;
volatile uint16_t r1_status_dropped __attribute__((section(".r1.status.dropped"),aligned(2)))=0;
struct r1_status_record { uint32_t packed,timestamp; };
struct r1_status_record r1_status_records[16] __attribute__((section(".r1.status.records"),aligned(4)))={0};
volatile uint8_t r1_device_state_byte_2c __attribute__((section(".r1.status.device2c")))=0;
volatile uint8_t r1_device_state_byte_2d __attribute__((section(".r1.status.device2d")))=0;
extern volatile uint16_t r1_connection_field8,r1_connection_field10;
extern uint32_t r1_advertising_configuration_byte_get(void);
extern uint32_t r1_battery_runtime_update_service(void);
extern uint32_t r1_structured_log_local_timestamp(void);
extern void vPortEnterCritical(void),vPortExitCritical(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
uint32_t r1_device_state_byte_2d_get(void) { return r1_device_state_byte_2d; }
uint32_t r1_peer_channel_count(void)
{
    uint32_t count=r1_connection_field8!=UINT16_MAX;
    count+=r1_connection_field10!=UINT16_MAX;return count;
}
uint32_t r1_charge_state_byte_get(void)
{
    if (r1_advertising_configuration_byte_get()==0x55) (void)r1_battery_runtime_update_service();
    uint8_t state=r1_device_state_byte_2c;return state ? state : 1;
}
uint32_t r1_status_record_ring_publish(uint32_t kind,uint32_t event,uint32_t value,uint32_t detail)
{
    uint32_t packed=0xau|((kind&3u)<<4)|((event&63u)<<6)|((value&63u)<<12)|((detail&7u)<<18);
    uint32_t device=r1_device_state_byte_2d_get();packed|=(device&3u)<<21;
    uint32_t peers=r1_peer_channel_count();packed|=(peers&3u)<<23;
    uint32_t charge=r1_charge_state_byte_get();packed|=(charge&127u)<<25;
    uint32_t timestamp=r1_structured_log_local_timestamp();
    vPortEnterCritical();
    uint8_t next=(uint8_t)((r1_status_write_index+1u)&15u);
    if (next==r1_status_read_index) r1_status_dropped=(uint16_t)(r1_status_dropped+1u);
    else {
        struct r1_status_record *slot=&r1_status_records[r1_status_write_index];
        slot->packed=packed;slot->timestamp=timestamp;r1_status_write_index=next;
    }
    vPortExitCritical();
    return r1_event_publish(0x2003,0,0);
}
