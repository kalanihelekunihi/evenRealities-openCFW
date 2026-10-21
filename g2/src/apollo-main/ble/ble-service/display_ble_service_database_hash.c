/* Native Cordio AppDiscReadDatabaseHash at 0x5336e0. */
#include <stdint.h>
extern volatile uint8_t audio_ble_trace_level_cell;
extern uint8_t audio_ble_subsystem_rows_200733fc[];
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern void audio_ble_attc_read_by_type_56c4ee(uint8_t,uint16_t,uint16_t,uint8_t,
                                                  const uint8_t *,uint32_t);
static void database_hash_log(uint8_t level,uint8_t connection) {
    static const char module[]="APP";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_disc.c";
    static const char name[]="AppDiscReadDatabaseHash";
    static const char message[]="Invalid connId in AppDiscReadDatabaseHash: %d";
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,module,source,name,0x46au,message,connection);
}
void audio_ble_service_discovery_followup_5336e0(uint8_t connection) {
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",app[]="APP",hci[]="HCI";
    static const char message[]="Invalid connId in AppDiscReadDatabaseHash: %d";
    static const uint8_t database_hash_uuid[2]={0x2au,0x2bu}; /* ROM 0x78f54e */
    if(connection==0u) {
        if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,error,3u)!=0) {
            if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,warn,4u)!=0) {
                if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,info,4u)!=0) {
                    if(audio_ble_trace_level_cell==0u) {
                        if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(app,hci,3u)!=0)
                            audio_ble_wsf_trace(warn,message,connection);
                    } else database_hash_log(4u,connection);
                } else database_hash_log(3u,connection);
            } else database_hash_log(2u,connection);
        } else database_hash_log(1u,connection);
        return;
    }
    uint8_t *row=audio_ble_subsystem_rows_200733fc+((uint32_t)connection-1u)*16u;
    if(row[11u]!=0u)return;
    row[11u]=3u;
    audio_ble_attc_read_by_type_56c4ee(connection,1u,0xffffu,2u,database_hash_uuid,0u);
}
