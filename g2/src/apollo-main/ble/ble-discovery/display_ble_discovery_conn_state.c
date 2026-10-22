/* Native Cordio AppConnBonded query 0x4bad26 and DmConnSetIdle 0x4b71dc. */
#include <stdint.h>
extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern uint8_t audio_ble_dm_conn_rows_200712a4[];
extern uint8_t audio_ble_connection_record_active(uint8_t); /* selected DmConnInUse */
extern volatile uint8_t audio_ble_trace_level_cell;
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);

static void app_invalid_conn(void) {
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",hci[]="HCI",app[]="APP";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_main.c";
    static const char name[]="AppCheckBonded",message[]="Invalid connId in AppConnBonded: %d";
    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,error,3)!=0){
        if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,warn,4)!=0){
            if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,info,4)!=0){
                if(audio_ble_trace_level_cell==0){
                    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(app,hci,3)!=0)
                        audio_ble_wsf_trace(warn,message,0);
                }else if((audio_log_flags()&2u)!=0u)
                    audio_log_extended(4,app,source,name,0xb5u,message,0);
            }else if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3,app,source,name,0xb5u,message,0);
        }else if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2,app,source,name,0xb5u,message,0);
    }else if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1,app,source,name,0xb5u,message,0);
}

uint8_t audio_ble_connection_is_active_4bad26(uint8_t connection) {
    if(connection==0){app_invalid_conn();return 0;}
    return audio_ble_discovery_connection_records_200717b0[((uint32_t)connection-1u)*0x30u+5u];
}


