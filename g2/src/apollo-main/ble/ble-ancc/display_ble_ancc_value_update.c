/* Native _ancsValueUpdate 0x4befce and its two RAM-backed guards. */
#include <stdint.h>
extern uint8_t *audio_ble_ancc_service_context; /* pointer cell 0x200748a0 */
extern uint8_t audio_ble_ancc_service_state[]; /* RAM base 0x200036c8 */
extern uint8_t audio_efs_transfer_state[]; /* base 0x20071cc8, flag +0x75 */
extern uint32_t audio_ble_ancc_connection_tick; /* 0x200742f4 */
extern uint32_t audio_ota_transfer_active(void); /* selected native 0x4487ac */
extern uint32_t g2_flashdb_candidate_tick(void); /* selected osKernelGetTickCount */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_ble_ancc_notification_value_update_4bee5a(uint8_t *,const uint8_t *);
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}

void audio_ble_ancc_value_update_4befce(const void *raw) {
    const uint8_t *event=(const uint8_t *)raw;
    const uint8_t *handles=audio_ble_ancc_service_context;
    uint16_t handle=rd16(event+10u);
    if(handle!=rd16(handles) && handle!=rd16(handles+6u) && handle!=rd16(handles+4u))return;
    if(audio_ble_ancc_service_state[0]!=1u || audio_ota_transfer_active()!=0u ||
       audio_efs_transfer_state[0x75u]==1u)return;
    if((uint32_t)(g2_flashdb_candidate_tick()-audio_ble_ancc_connection_tick)<5000u){
        static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ancc\\profile_ancc.c";
        static const char message[]="connect time is less than 5000ms, can't rx msg";
        static const char compact[]="[ble.ancc]connect time is less than 5000ms, can't rx msg";
        if(audio_log_level()&2u)
            audio_log_extended(4u,"ble.ancc",path,"_ancsValueUpdate",0x1d4u,message);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x10000000u,compact,compact);
    }else audio_ble_ancc_notification_value_update_4bee5a(audio_ble_ancc_service_context,event);
}
