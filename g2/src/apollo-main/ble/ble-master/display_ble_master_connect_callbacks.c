/* Native delayed callback bodies 0x4a01fc and 0x4bc418. */
#include <stdint.h>
extern uint8_t *audio_ble_master_context; /* product pointer cell 0x200742fc */
extern uint8_t audio_ble_controller[]; /* direct product struct 0x200727f0; getter returns address */
extern void *audio_wsf_msg_alloc(uint16_t);
extern void audio_wsf_msg_send(uint8_t,void *);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char master_module[]="ble.master";
static const char master_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
/* Stock 0x4A01FC (_masterConnectCancel) */
void audio_ble_master_disconnect_delayed(uint32_t connection) {
    if(audio_log_level()&2u)
      audio_log_extended(4u,master_module,master_source,"_masterConnectCancel",0x1c1u,"_masterConnectCancel");
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x10000000u,"[ble.master]_masterConnectCancel","[ble.master]_masterConnectCancel");
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(12u);
    if(message!=0) {
      if(audio_log_level()&2u)
        audio_log_extended(4u,master_module,master_source,"_masterConnectCancel",0x1c4u,
          "pMsg->hdr.event = EVEN_MASTER_CONNECT_CANCEL_EVT");
      if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10000000u,
          "[ble.master]pMsg->hdr.event = EVEN_MASTER_CONNECT_CANCEL_EVT",
          "[ble.master]pMsg->hdr.event = EVEN_MASTER_CONNECT_CANCEL_EVT");
      message[2]=0xb0u;
      *(uint16_t *)(void *)message=(uint16_t)((uint16_t)connection&0xffu);
      *(uint16_t *)(void *)(message+8u)=0u;
      audio_wsf_msg_send(audio_ble_master_context[0x56u],message);
    }
}
uint32_t audio_ble_master_success_delayed(uint32_t notification) {
    uint8_t *controller=audio_ble_controller;
    if(controller==0 || controller[0x56u]==0u) {
      if(audio_log_level()&2u)
        audio_log_extended(1u,"pb.devc",
          "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_dev_config\\pb_service_pair_mgr.c",
          "PB_TxEncodeNotifyRingConnectInfo",0x1d4u,
          "PB_TxEncodeNotifyRingConnectInfo: pBleCb or handlerId is NULL");
      if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x04000000u,
          "[pb.devc]PB_TxEncodeNotifyRingConnectInfo: pBleCb or handlerId is NULL",
          "[pb.devc]PB_TxEncodeNotifyRingConnectInfo: pBleCb or handlerId is NULL");
      return UINT32_MAX;
    }
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(12u);
    if(message==0) return UINT32_MAX;
    message[2]=0xbbu;
    *(uint16_t *)(void *)message=0u;
    *(uint16_t *)(void *)(message+8u)=(uint16_t)(notification&0xffu);
    audio_wsf_msg_send(controller[0x56u],message);
    return 0u;
}
