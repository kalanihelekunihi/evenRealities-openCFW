/* Native Cordio appDiscRestartDiscovery 0x531f20. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_rows_200733fc[];
extern const void *audio_ble_profile_dispatch_slot; /* producer 0x535488 */
extern uint8_t *audio_ble_pair_record(uint8_t);
extern void audio_ble_pair_record_clear_a(uint8_t *,uint8_t);
extern void audio_ble_pair_record_attach(uint8_t *,uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_ble_service_discovery_start(uint8_t);
extern volatile uint8_t audio_ble_trace_level_cell;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static uint32_t ptr32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void invalid_connection(void){
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",app[]="APP",hci[]="HCI";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_disc.c";
    static const char name[]="appDiscRestartDiscovery",message[]="Invalid connId in appDiscRestartDiscovery: %d";
    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,error,3)!=0){
        if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,warn,4)!=0){
            if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,info,4)!=0){
                if(audio_ble_trace_level_cell==0){
                    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(app,hci,3)!=0)
                        audio_ble_wsf_trace(warn,message,0);
                }else if((audio_log_flags()&2u)!=0u)
                    audio_log_extended(4,app,source,name,0xc3u,message,0);
            }else if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3,app,source,name,0xc3u,message,0);
        }else if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2,app,source,name,0xc3u,message,0);
    }else if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1,app,source,name,0xc3u,message,0);
}
void audio_ble_service_discovery_restart_531f20(uint8_t connection){
    if(connection==0u){invalid_connection();return;}
    uint8_t *row=audio_ble_subsystem_rows_200733fc+((uint32_t)connection-1u)*16u;
    row[8]=row[9]=row[13]=row[14]=0u;
    const uint32_t destination=ptr32(row+4);
    if(destination!=0u){
        audio_uart_buffer_zero((void *)(uintptr_t)destination,(uint32_t)row[10]*2u,0u);
        uint8_t *record=audio_ble_pair_record(connection);
        if(record!=0u){
            audio_ble_pair_record_clear_a(record,0u);
            audio_ble_pair_record_attach(record,destination);
        }
    }
    if(row[11]==2u)row[14]=1u;
    else if(((const uint8_t *)audio_ble_profile_dispatch_slot)[0]==0u || row[12]!=0u)
        audio_ble_service_discovery_start(connection);
}
