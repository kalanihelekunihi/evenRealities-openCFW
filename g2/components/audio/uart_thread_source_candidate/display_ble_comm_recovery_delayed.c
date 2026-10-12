/* Native PB_TxEncodeNotifySecAuth 0x4bb92c, delayed security notification. */
#include <stdint.h>
extern uint8_t audio_ble_controller[]; /* direct product struct at 0x200727f0 */
extern uint8_t *WsfMsgAlloc(uint16_t length);
extern void WsfMsgSend(uint8_t handler,void *message);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
uint32_t audio_ble_comm_recovery_delayed(uint16_t notification)
{
    static const char module[]="pb.devc";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_dev_config\\pb_service_pair_mgr.c";
    static const char function[]="PB_TxEncodeNotifySecAuth";
    static const char message[]="PB_TxEncodeNotifySecAuth: pBleCb or handlerId is NULL";
    static const char compact[]="[pb.devc]PB_TxEncodeNotifySecAuth: pBleCb or handlerId is NULL";
    uint8_t *const controller=audio_ble_controller;
    if (!controller || !controller[0x56u]) {
        if (audio_log_flags()&2u)
            audio_log_extended(1u,module,source,function,0xb7u,message);
        uint32_t flags=audio_log_flags();
        if ((flags&1u)||((flags=audio_log_flags())&4u))
            (void)compressed_log_output(0x04000000u,compact,compact);
        return UINT32_MAX;
    }
    uint8_t *message_buffer=WsfMsgAlloc(12u);
    if (!message_buffer) return UINT32_MAX;
    message_buffer[2u]=0xbau;
    message_buffer[0u]=0u;
    message_buffer[1u]=0u;
    message_buffer[8u]=(uint8_t)notification;
    message_buffer[9u]=0u;
    WsfMsgSend(controller[0x56u],message_buffer);
    return 0u;
}
