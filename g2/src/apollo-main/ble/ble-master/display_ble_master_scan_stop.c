/* Apollo appMasterScanStop diagnostic 0x50367c and count getter 0x503d14. */
#include <stdint.h>

extern volatile uint8_t audio_ble_subsystem_state_20071670[];
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,...);

static const char error_label[]="ERR";
static const char info_label[]="INFO";
static const char warn_label[]="WARN";
static const char app_label[]="APP";
static const char hci_label[]="HCI";
static const char message_text[]="Scan results: %d";
static const char function_name[]="appMasterScanStop";
static const char source_path[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_master.c";

extern uint8_t audio_ble_master_scan_count_503d14(void); /* opencfw U5: now provided by the Cordio unit */

void audio_ble_master_event_50367c(void *event,void *record)
{
    (void)record;
    if (((const uint8_t *)event)[3]!=0u) return;
    if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
        audio_l2c_strncmp(info_label,error_label,3u)!=0) {
        if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
            audio_l2c_strncmp(info_label,warn_label,4u)!=0) {
            if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
                audio_l2c_strncmp(info_label,info_label,4u)!=0) {
                if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u) {
                    if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
                        audio_l2c_strncmp(app_label,hci_label,3u)!=0)
                        audio_ble_wsf_trace(info_label,message_text,
                                            audio_ble_master_scan_count_503d14());
                } else if (audio_log_flags()&2u) {
                    audio_log_extended(4u,app_label,source_path,function_name,
                                       0x112u,message_text,
                                       audio_ble_master_scan_count_503d14());
                }
            } else if (audio_log_flags()&2u) {
                audio_log_extended(3u,app_label,source_path,function_name,
                                   0x112u,message_text,
                                   audio_ble_master_scan_count_503d14());
            }
        } else if (audio_log_flags()&2u) {
            audio_log_extended(2u,app_label,source_path,function_name,
                               0x112u,message_text,
                               audio_ble_master_scan_count_503d14());
        }
    } else if (audio_log_flags()&2u) {
        audio_log_extended(1u,app_label,source_path,function_name,
                           0x112u,message_text,
                           audio_ble_master_scan_count_503d14());
    }
}
