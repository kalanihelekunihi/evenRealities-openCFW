/* Apollo Cordio AttsCsfSetClientChangeAwareState 0x52d090. */
#include <stdint.h>

extern volatile uint8_t audio_ble_csf_state_20073e04[];
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,...);

static const char error_label[]="ERR";
static const char warn_label[]="WARN";
static const char info_label[]="INFO";
static const char att_label[]="ATT";
static const char hci_label[]="HCI";
static const char source_path[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_csf.c";
static const char function_name[]="AttsCsfSetClientChangeAwareState";
static const char changed[]="ConnId %d change aware state is %d";

void audio_ble_dm_service_state_reset_52d090(uint8_t connection,uint8_t state)
{
    if (connection==0u) {
        for (uint8_t i=0u;i<3u;++i) {
            volatile uint8_t *slot=audio_ble_csf_state_20073e04+(uint32_t)i*2u+1u;
            *slot=(*slot==2u)?1u:state;
        }
        return;
    }
    audio_ble_csf_state_20073e04[(uint32_t)connection*2u-1u]=state;
    if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
        audio_l2c_strncmp(info_label,error_label,3u)!=0) {
        if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
            audio_l2c_strncmp(info_label,warn_label,4u)!=0) {
            if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
                audio_l2c_strncmp(info_label,info_label,4u)!=0) {
                if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u) {
                    if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
                        audio_l2c_strncmp(att_label,hci_label,3u)!=0)
                        audio_ble_wsf_trace(info_label,changed,connection,state);
                } else if (audio_log_flags()&2u) {
                    audio_log_extended(4u,att_label,source_path,function_name,
                                       0x123u,changed,connection,state);
                }
            } else if (audio_log_flags()&2u) {
                audio_log_extended(3u,att_label,source_path,function_name,
                                   0x123u,changed,connection,state);
            }
        } else if (audio_log_flags()&2u) {
            audio_log_extended(2u,att_label,source_path,function_name,
                               0x123u,changed,connection,state);
        }
    } else if (audio_log_flags()&2u) {
        audio_log_extended(1u,att_label,source_path,function_name,
                           0x123u,changed,connection,state);
    }
}
