/* Native APP_MasterSetPhyEvent 0x4a2254, Cordio message allocation
 * and master-context dispatch with authenticated log strings. */
#include <stdint.h>
extern uint8_t *audio_ble_master_context; /* live pointer cell RAM 0x200742fc */
extern void *audio_wsf_msg_alloc(uint16_t); /* selected 0x4bf99e */
extern void audio_wsf_msg_send(uint8_t,void *); /* selected 0x4bf9ba */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.master";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char fn[]="APP_MasterSetPhyEvent";
static const char message[]="APP_MasterSetPhyEvent triggered";
static const char short_message[]="[ble.master]APP_MasterSetPhyEvent triggered";
void audio_uart_ring_master_set_phy_event_4a2254(uint32_t unused) {
    (void)unused;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,fn,1204u,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,short_message,short_message);
    uint8_t *msg=(uint8_t *)audio_wsf_msg_alloc(12u);
    if(msg!=0) {
        msg[2]=0xb4u;
        *(uint16_t *)(void *)msg=audio_ble_master_context[0x55u];
        *(uint16_t *)(void *)(msg+8u)=0u;
        audio_wsf_msg_send(audio_ble_master_context[0x56u],msg);
    }
}
