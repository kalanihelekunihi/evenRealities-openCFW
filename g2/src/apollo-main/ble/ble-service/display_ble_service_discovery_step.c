/* Native Cordio appDiscCfgStart at 0x531bd4. */
#include <stdint.h>
extern volatile uint8_t audio_ble_trace_level_cell;
extern uint8_t audio_ble_subsystem_rows_200733fc[];
extern uintptr_t audio_ble_service_dispatch_20074348;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static void step_log(uint8_t level,uint8_t status) {
    static const char module[]="APP";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_disc.c";
    static const char name[]="appDiscCfgStart";
    static const char message[]="Invalid connId in appDiscCfgStart: %d, status: %d";
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,module,source,name,0x5du,message,0u,status);
}
void audio_ble_service_discovery_step_531bd4(uint8_t connection,uint8_t status) {
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",app[]="APP",hci[]="HCI";
    static const char message[]="Invalid connId in appDiscCfgStart: %d, status: %d";
    if(connection==0u) {
        if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,error,3u)!=0) {
            if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,warn,4u)!=0) {
                if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,info,4u)!=0) {
                    if(audio_ble_trace_level_cell==0u) {
                        if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(app,hci,3u)!=0)
                            audio_ble_wsf_trace(warn,message,0u,status);
                    } else step_log(4u,status);
                } else step_log(3u,status);
            } else step_log(2u,status);
        } else step_log(1u,status);
    } else if(status<8u) {
        ((void (*)(uint8_t,uint8_t))audio_ble_service_dispatch_20074348)(connection,6u);
    } else if(status==8u && audio_ble_subsystem_rows_200733fc[((uint32_t)connection-1u)*16u+8u]==0u) {
        ((void (*)(uint8_t,uint8_t))audio_ble_service_dispatch_20074348)(connection,7u);
    }
}
