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

static const char error_label[] = "ERR";
static const char app_label[] = "APP";
static const char hci_label[] = "HCI";
static const char info_label[] = "INFO";
static const char warn_label[] = "WARN";
static const char db_hash_updated[] = "Database hash updated";
static const char db_hash_function[] = "appServerHandleDbHashUpdate";
static const char db_hash_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_server.c";

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

void audio_ble_comm_dm_disconnect_5346e4(void *message)
{
    const uint8_t *bytes = (const uint8_t *)message;
    uint32_t source_address = *(const uint32_t *)(const void *)(bytes + 4u);
    uint32_t old_hash = audio_ble_dm_database_hash_get_47b45a();
    if (old_hash != 0u &&
        g2_lfs_memcmp((const void *)(uintptr_t)source_address,
                      (const void *)(uintptr_t)old_hash,16u) != 0)
        old_hash = 0u;
    if (old_hash != 0u) return;

    audio_ble_dm_database_hash_copy_47b468((const void *)(uintptr_t)source_address);
    audio_ble_dm_connection_state_set(0u,3u);
    audio_ble_dm_service_state_reset_52d090(0u,3u);

    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
        audio_l2c_strncmp(info_label,error_label,3u) != 0) {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_l2c_strncmp(info_label,warn_label,4u) != 0) {
            if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                audio_l2c_strncmp(info_label,info_label,4u) != 0) {
                if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u) {
                    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                        audio_l2c_strncmp(app_label,hci_label,3u) != 0)
                        audio_ble_wsf_trace(info_label,db_hash_updated);
                } else if (audio_log_flags() & 2u) {
                    audio_log_extended(4u,app_label,db_hash_path,db_hash_function,
                                       0xbdu,db_hash_updated);
                }
            } else if (audio_log_flags() & 2u) {
                audio_log_extended(3u,app_label,db_hash_path,db_hash_function,
                                   0xbdu,db_hash_updated);
            }
        } else if (audio_log_flags() & 2u) {
            audio_log_extended(2u,app_label,db_hash_path,db_hash_function,
                               0xbdu,db_hash_updated);
        }
    } else if (audio_log_flags() & 2u) {
        audio_log_extended(1u,app_label,db_hash_path,db_hash_function,
                           0xbdu,db_hash_updated);
    }
    (void)audio_ble_dm_advertising_resume_4b5a44(0u,1u,0xffffu,0u);
}

uint32_t audio_ble_dm_connection_record_get(uint8_t connection)
{
    const uint8_t *record = audio_ble_discovery_connection_records_200717b0
                          + ((uint32_t)connection - 1u) * 0x30u;
    return *(const uint32_t *)(const void *)record;
}

void audio_ble_dm_connection_state_set(uint32_t record, uint8_t state)
{
    if (record != 0u) {
        *(volatile uint8_t *)(uintptr_t)(record + 0x84u) = state;
        return;
    }
    for (unsigned i = 0; i < 10u; ++i)
        audio_ble_dm_conn_state_table_20067a30[i * 200u + 0x84u] = state;
}

void audio_ble_comm_dm_connected_53480c(const void *message)
{
    const uint8_t *bytes = (const uint8_t *)message;
    uint16_t event = (uint16_t)bytes[10] | ((uint16_t)bytes[11] << 8);
    if (event == 0x12u) {
        uint8_t connection = bytes[0];
        uint32_t record = audio_ble_dm_connection_record_get(connection);
        if (record != 0u) audio_ble_dm_connection_state_set(record, 0u);
    }
}

void audio_ble_comm_dm_dispatch_b(void *message)
{
    uint8_t event = ((const uint8_t *)message)[2];
    if (event == 0x12u)
        audio_ble_comm_dm_connected_53480c(message);
    else if (event == 0x15u)
        audio_ble_comm_dm_disconnect_5346e4(message);
}
