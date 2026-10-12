/* Native Cordio l2cRxSignalingPkt 0x53076e, including role failure logging. */
#include <stdint.h>
extern uint8_t audio_ble_l2c_state[0x30u];
extern uint8_t DmConnIdByHandle(uint16_t);
extern uint8_t DmConnRole(uint8_t);
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_hci_wsf_trace(const char *,const char *,...);
typedef void (*l2c_rx_cb)(uint32_t,uint32_t,uint8_t *);
static const char err[]="ERR",warn[]="WARN",info[]="INFO",module[]="L2C",hci[]="HCI";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\l2c\\l2c_main.c";
static const char function[]="l2cRxSignalingPkt";
static const char message[]="Invalid role configuration: role=%d";
static void invalid_role(uint8_t role) {
    uint8_t level;
    if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(err,err,3u)==0) level=1u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(err,warn,4u)==0) level=2u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(err,info,4u)==0) level=3u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u) level=4u;
    else {
        if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(module,hci,3u)!=0)
            audio_ble_hci_wsf_trace(err,message,role);
        return;
    }
    if((audio_log_flags()&2u)!=0u)audio_log_extended(level,module,source,function,0x80u,message,role);
}
void audio_ble_l2c_rx_signaling_53076e(uint16_t handle,uint32_t length,uint8_t *packet) {
    if((length&0xffffu)<=3u)return;
    uint8_t conn=DmConnIdByHandle(handle);
    if(conn==0u)return;
    uint8_t role=DmConnRole(conn);
    if(role==0u) {
        l2c_rx_cb cb=*(l2c_rx_cb *)(void *)(audio_ble_l2c_state+24u);
        if(cb!=0) {cb(handle,length&0xffffu,packet);return;}
    } else if(role==1u) {
        l2c_rx_cb cb=*(l2c_rx_cb *)(void *)(audio_ble_l2c_state+28u);
        if(cb!=0) {cb(handle,length&0xffffu,packet);return;}
    }
    invalid_role(role);
}
