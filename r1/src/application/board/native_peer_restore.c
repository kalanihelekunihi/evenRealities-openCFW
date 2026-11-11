/* Stock persistent peer restore: 0x736b8, 0x73778, 0x737c8,
 * 0x3d764 and 0x4cb58. Reuse canonical KV and address owners. */
#include <stdint.h>
#include <string.h>
#include "native_kv_class.h"
#include "native_battery_memory.h"
#include "native_ble_identity.h"
extern void *volatile r1_device_info_record_kv_handle;
extern uint32_t r1_nv_modules_idle_check(void);
void r1_config_record_refresh(void)
{
    uint8_t record[52]={0};
    (void)r1_kv_class_read(r1_device_info_record_kv_handle,record,52);
    if (read32(record+20)!=UINT32_C(0x484d4143)) {
        memset(record+8,255,6);
        memset(record+14,255,6);
        write32(record+20,UINT32_C(0x484d4143));
        record[24]&=(uint8_t)~4u;
        (void)r1_kv_class_write(r1_device_info_record_kv_handle,record,52);
        (void)r1_nv_modules_idle_check();
    }
}
uint32_t r1_peer_record_flag_get(void)
{
    uint8_t record[52]={0};
    (void)r1_kv_class_read(r1_device_info_record_kv_handle,record,52);
    return (record[24]>>2)&1u;
}
void r1_kv_dev_info_pair_get(void *first,void *second)
{
    uint8_t record[52]={0};
    (void)r1_kv_class_read(r1_device_info_record_kv_handle,record,52);
    if (first) memcpy(first,record+8,6);
    if (second) memcpy(second,record+14,6);
}
void r1_peer_address_flag_update(volatile uint8_t *record)
{
    static const uint8_t empty_ff[6]={255,255,255,255,255,255};
    static const uint8_t empty_zero[6]={0};
    uint32_t populated=memcmp((const void *)(record+1),empty_ff,6)!=0 &&
                       memcmp((const void *)(record+1),empty_zero,6)!=0;
    uint8_t low=record[0]&1u;
    record[0]=(uint8_t)(low+(populated ? 0x14u:0u));
}
void r1_peer_record_commit(void)
{
    r1_config_record_refresh();
    if (!r1_peer_record_flag_get()) return;
    uint8_t first[6]={0},second[6]={0};
    r1_kv_dev_info_pair_get(first,second);
    for (uint32_t i=0;i<6;i++) r1_ble_phone_peer_address[i+1]=first[i];
    for (uint32_t i=0;i<6;i++) r1_ble_glasses_peer_address[i+1]=second[i];
    r1_peer_address_flag_update(r1_ble_phone_peer_address);
    r1_peer_address_flag_update(r1_ble_glasses_peer_address);
}
