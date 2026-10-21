/* Native callbacks 0x46f098, 0x46f350 and 0x46effc. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint8_t *audio_ble_slave_mode_context; /* pointer cell 0x20074330 */
extern uint8_t *audio_ble_profile_connection_context; /* pointer cell 0x2007432c */
extern void audio_ble_slave_security_state(uint8_t); /* 0x4b82e8 */
extern void *audio_wsf_msg_alloc(uint16_t);
extern void audio_wsf_msg_send(uint8_t,void *);
static const char module[]="ble.Slave";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c";
#define LOG(level,function,line,mask,plain,short_text,...) do { \
 if(audio_log_flags()&2u) audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(mask,short_text,short_text,##__VA_ARGS__); \
} while(0)
void audio_ble_slave_open_followup(void) {
    LOG(2u,"APP_BleSlaveWaitSecurityRequestEvt",0x2f9u,0x08000000u,
        "WaitSecurityRequestCmd failed disconnect",
        "[ble.Slave]WaitSecurityRequestCmd failed disconnect");
}
void audio_ble_slave_open_watchdog(uint32_t event) {
    LOG(4u,"_bleSlaveSyncConnectEvt",0x332u,0x10400000u,
        "_bleSlaveSyncConnectEvt event = %d",
        "[ble.Slave]_bleSlaveSyncConnectEvt event = %d",event&0xffu);
    audio_ble_slave_security_state((uint8_t)event);
}
void audio_ble_slave_disconnect_followup(uint32_t trusted) {
    audio_ble_slave_mode_context[0x20u]=(trusted!=0u);
    LOG(4u,"APP_SlaveStartSecurityRequestEvent",0x2e4u,0x10400000u,
        "STrustedDevices = %d","[ble.Slave]STrustedDevices = %d",
        audio_ble_slave_mode_context[0x20u]);
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(12u);
    if(message) {
        message[2u]=0xb5u;
        uint16_t id=audio_ble_profile_connection_context[0x54u];
        message[0u]=(uint8_t)id;
        message[1u]=(uint8_t)(id>>8);
        message[8u]=1u;
        message[9u]=0u;
        audio_wsf_msg_send(audio_ble_profile_connection_context[0x56u],message);
    }
}
