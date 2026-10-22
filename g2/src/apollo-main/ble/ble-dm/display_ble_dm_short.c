/* Apollo BLE DM short path: 0x53484c, 0x53480c, 0x4bb07c, 0x47b438. */
#include <stdint.h>

extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern uint8_t audio_ble_dm_conn_state_table_20067a30[];
extern uint8_t audio_ble_dm_database_hash_20068215[];
extern int32_t g2_lfs_memcmp(const void *, const void *, uint32_t);
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *, const char *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,...);
extern void audio_ble_dm_service_state_reset_52d090(uint8_t,uint8_t);
extern uint32_t audio_ble_dm_advertising_resume_4b5a44(uint8_t,uint16_t,uint16_t,uint32_t);
void audio_ble_dm_connection_state_set(uint32_t record, uint8_t state);


uint32_t audio_ble_dm_database_hash_get_47b45a(void)
{
    return (uint32_t)(uintptr_t)audio_ble_dm_database_hash_20068215;
}

void audio_ble_dm_database_hash_copy_47b468(const void *source)
{
    if (source == 0) return;
    const uint8_t *from = (const uint8_t *)source;
    for (unsigned i = 0; i < 16u; ++i)
        audio_ble_dm_database_hash_20068215[i] = from[i];
}



/* Stock 0x47B438 (AppDbSetClientChangeAwareState; upstream third-party/upstream/cordio/ble-profiles/sources/af/common/app_db.c) */
void audio_ble_dm_connection_state_set(uint32_t record, uint8_t state)
{
    if (record != 0u) {
        *(volatile uint8_t *)(uintptr_t)(record + 0x84u) = state;
        return;
    }
    for (unsigned i = 0; i < 10u; ++i)
        audio_ble_dm_conn_state_table_20067a30[i * 200u + 0x84u] = state;
}


