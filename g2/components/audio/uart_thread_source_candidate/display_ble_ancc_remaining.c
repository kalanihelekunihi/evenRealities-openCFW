/* ANCC delayed action and attribute write, native 0x4bea7a/0x4beae8.
 * Native IAR source strings and the Ambiq ANCC packet layout are retained. */
#include <stdint.h>
extern uint8_t audio_ble_ancc_state[]; /* live 0x200695c8 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgSend(uint8_t,void *);
extern void audio_ble_attc_write_request(uint8_t,uint16_t,uint16_t,const uint8_t *); /* native 0x4b579c */

void audio_ble_ancc_get_next_delayed_4bea7a(uint32_t event) {
    static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ancc\\profile_ancc.c";
    static const char fn[]="_anccGetNextNotificationHandler";
    static const char message[]="_anccGetNextNotificationHandler %d";
    static const char compact[]="[ble.ancc]_anccGetNextNotificationHandler %d";
    if(audio_log_level()&2u)
        audio_log_extended(4u,"ble.ancc",path,fn,0xd4u,message,event&0xffu);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,compact,compact,event&0xffu);
    uint8_t *msg=(uint8_t *)WsfMsgAlloc(12u);
    if(msg!=0){
        msg[0]=audio_ble_ancc_state[0];
        msg[1]=0u;
        msg[2]=(uint8_t)event;
        WsfMsgSend(audio_ble_ancc_state[1],msg);
    }
}

void audio_ble_ancc_get_notification_attribute_4beae8(uint32_t handle_list,uint32_t uid) {
    const uint8_t *handles=(const uint8_t *)(uintptr_t)handle_list;
    uint16_t control=(uint16_t)handles[4]|((uint16_t)handles[5]<<8);
    if(control==0u)return;
    uint8_t packet[19]={
        0u,(uint8_t)uid,(uint8_t)(uid>>8),(uint8_t)(uid>>16),(uint8_t)(uid>>24),
        0u,1u,0u,1u,2u,0u,1u,3u,0u,1u,4u,5u,6u,7u
    };
    audio_ble_attc_write_request(audio_ble_ancc_state[0],control,19u,packet);
}
