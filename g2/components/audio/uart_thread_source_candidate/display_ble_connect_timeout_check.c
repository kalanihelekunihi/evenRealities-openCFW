/* Product APP_BleConnectTimeoutCheckEvt 0x4b81b8: diagnostic timer callback. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
void audio_ble_comm_link_delayed(void)
{
    static const char module[]="ble.comm";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble.c";
    static const char function[]="APP_BleConnectTimeoutCheckEvt";
    static const char message[]="APP_BleConnectTimeoutCheckEvt failed disconnect";
    static const char compact[]="[ble.comm]APP_BleConnectTimeoutCheckEvt failed disconnect";
    if (audio_log_flags()&2u)
        audio_log_extended(2u,module,source,function,0x392u,message);
    uint32_t flags=audio_log_flags();
    if ((flags&1u)||((flags=audio_log_flags())&4u))
        (void)compressed_log_output(0x08000000u,compact,compact);
}
