/* Native Thread_MsgPbNotifyByBle 0x475c1a. The native left-role branch
 * contains a constant-true test at 0x475c70, so its other arm is dead. */
#include <stdint.h>
extern uint32_t audio_ota_transfer_active(void); /* native 0x4487ac */
extern uint32_t audio_app_is_left_slave_role(void); /* native 0x46f258 */
extern uint32_t audio_app_is_local_slave_cmd_role(void); /* native 0x46f1d0 */
extern uint32_t audio_ble_msg_tx(uint8_t,uint8_t,uint8_t,uint8_t,
                                 const void *,uint16_t); /* native 0x47564e */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.msgtx";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_msgtx.c";
static const char function[]="Thread_MsgPbNotifyByBle";
static const char ota[]="OTA is going, pb notify failed";
static const char ota_short[]="[ble.msgtx]OTA is going, pb notify failed";
static const char left[]="------left can't notify pb------";
static const char left_short[]="[ble.msgtx]------left can't notify pb------";
static const char cmd[]="------not as cmd role------";
static const char cmd_short[]="[ble.msgtx]------not as cmd role------";
uint32_t audio_settings_notify_ble(uint8_t type,uint8_t command,
                                   const void *payload,uint32_t length) {
    if(audio_ota_transfer_active()!=0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,452u,ota);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,ota_short,ota_short);
        return 0u;
    }
    if(audio_app_is_left_slave_role()!=0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,464u,left);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,left_short,left_short);
        return 8u;
    }
    if(audio_app_is_local_slave_cmd_role()==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,469u,cmd);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,cmd_short,cmd_short);
        return 8u;
    }
    return audio_ble_msg_tx(0u,1u,type,command,payload,(uint16_t)length);
}
