/* Native Thread_MsgPbNotifyByBleDirect 0x475aa6. */
#include <stdint.h>
extern uint32_t audio_ota_transfer_active(void); /* selected 0x4487ac */
extern uint32_t audio_ble_msg_tx(uint8_t,uint8_t,uint8_t,uint8_t,const void *,uint16_t); /* selected 0x47564e */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
uint32_t audio_ble_notify_direct_475aa6(uint8_t type,uint8_t command,const void *payload,uint16_t length)
{
    static const char module[]="ble.msgtx";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_msgtx.c";
    static const char function[]="Thread_MsgPbNotifyDirectByBle";
    static const char message[]="OTA is going, pb notify direct failed";
    static const char compact[]="[ble.msgtx]OTA is going, pb notify direct failed";
    if (audio_ota_transfer_active()!=0u) {
        if (audio_log_flags()&2u)
            audio_log_extended(4u,module,source,function,0x1a2u,message);
        uint32_t flags=audio_log_flags();
        if ((flags&1u)||((flags=audio_log_flags())&4u))
            (void)compressed_log_output(0x10000000u,compact,compact);
        return 0u;
    }
    return audio_ble_msg_tx(0u,1u,type,command,payload,length);
}
