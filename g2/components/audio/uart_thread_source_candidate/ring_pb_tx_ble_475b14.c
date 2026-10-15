/* Stock Apollo Thread_MsgPbTxByBle 0x475b14. */
#include <stdint.h>

extern uint32_t audio_ota_transfer_active(void); /* selected 0x4487ac */
extern uint32_t audio_app_is_left_slave_role(void); /* selected 0x46f258 */
extern uint32_t audio_ble_msg_tx(uint8_t,uint8_t,uint8_t,uint8_t,
                                  const void *,uint16_t); /* selected 0x47564e */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...); /* selected 0x43d574 */
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...); /* selected 0x43ce9e */

static const char module[]="ble.msgtx";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_msgtx.c";
static const char function[]="Thread_MsgPbTxByBle";
static const char ota_message[]="OTA is going, pb tx failed";
static const char ota_short[]="[ble.msgtx]OTA is going, pb tx failed";
static const char left_message[]="------left can't send pb------";
static const char left_short[]="[ble.msgtx]------left can't send pb------";

uint32_t audio_ring_pb_tx_ble_475b14(uint32_t type,uint32_t command,
                                      const void *payload,uint32_t length) {
    if(audio_ota_transfer_active()!=0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,0x1acu,ota_message);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,ota_short,ota_short);
        return 0u;
    }
    if(audio_app_is_left_slave_role()!=0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,0x1b9u,left_message);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,left_short,left_short);
        return 8u;
    }
    return audio_ble_msg_tx(0u,0u,(uint8_t)type,(uint8_t)command,
                            payload,(uint16_t)length);
}
