/* Apollo appConnReadRemoteFeatTimerStart, native 0x4bb25c. */
#include <stdint.h>

extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern uint8_t audio_ble_adv_handler_id_20074f92;
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,...);
extern void WsfTimerStartMs(void *,uint32_t);

static const char app_label[]="APP";
static const char hci_label[]="HCI";
static const char error_label[]="ERR";
static const char warn_label[]="WARN";
static const char info_label[]="INFO";
static const char message_text[]="Invalid connId in appConnReadRemoteFeatTimerStart: %d";
static const char function_name[]="appConnReadRemoteFeatTimerStart";
static const char source_path[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_main.c";

void audio_ble_master_child_4bb25c(uint32_t connection)
{
    uint32_t id=connection&0xffu;
    if (id!=0u) {
        uint8_t *timer=audio_ble_discovery_connection_records_200717b0+
            id*0x30u-0x10u;
        timer[12u]=audio_ble_adv_handler_id_20074f92;
        timer[10u]=2u;
        timer[8u]=(uint8_t)id;
        timer[9u]=0u;
        WsfTimerStartMs(timer,0x1eu);
        return;
    }
    if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
        audio_l2c_strncmp(warn_label,error_label,3u)!=0) {
        if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
            audio_l2c_strncmp(warn_label,warn_label,4u)!=0) {
            if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
                audio_l2c_strncmp(warn_label,info_label,4u)!=0) {
                if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u) {
                    if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
                        audio_l2c_strncmp(app_label,hci_label,3u)!=0)
                        audio_ble_wsf_trace(warn_label,message_text,id);
                } else if (audio_log_flags()&2u) {
                    audio_log_extended(4u,app_label,source_path,function_name,
                                       0x22cu,message_text,id);
                }
            } else if (audio_log_flags()&2u) {
                audio_log_extended(3u,app_label,source_path,function_name,
                                   0x22cu,message_text,id);
            }
        } else if (audio_log_flags()&2u) {
            audio_log_extended(2u,app_label,source_path,function_name,
                               0x22cu,message_text,id);
        }
    } else if (audio_log_flags()&2u) {
        audio_log_extended(1u,app_label,source_path,function_name,
                           0x22cu,message_text,id);
    }
}
