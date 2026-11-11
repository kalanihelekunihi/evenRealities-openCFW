/* Native AncsGetAppAttribute 0x4bebc4 and _rxSyncEventCallback 0x4bed0e. */
#include <stdint.h>
extern uint8_t audio_ble_ancc_state[]; /* live 0x200695c8 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern void audio_ble_attc_write_request(uint8_t,uint16_t,uint16_t,const uint8_t *); /* native 0x4b579c */
static const char module[]="ble.ancc";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ancc\\profile_ancc.c";
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}

/* Stock 0x4BEBC4 (AncsGetAppAttribute): command byte, NUL-terminated app ID
 * and a trailing zero attribute ID in a 64-byte stack frame, sent with
 * AttcWriteReq (which copies it). For an ID of 62 or more characters the stock
 * skipped the copy but still stored the trailing zero at packet[length+1] and
 * sent length+2 bytes, overrunning the 64-byte frame into its saved registers;
 * that case is not reproduced and sends nothing. */
void audio_ble_ancc_get_app_attribute_4bebc4(uint32_t handle_list,const char *app_id){
    const uint8_t *handles=(const uint8_t *)(uintptr_t)handle_list;
    uint8_t packet[64];
    uint16_t control=rd16(handles+4u);
    if(control==0u)return;
    uint8_t length=0u;
    do {length=(uint8_t)(length+1u);} while(app_id[(uint8_t)(length-1u)]!='\0');
    if(length>=63u)return;
    packet[0]=1u;
    (void)audio_queue_copy_bytes(packet+1u,app_id,length);
    packet[(uint32_t)length+1u]=0u;
    audio_ble_attc_write_request(audio_ble_ancc_state[0],control,(uint16_t)length+2u,packet);
}

uint32_t audio_ble_ancc_rx_sync_callback_4bed0e(uint32_t status){
    static const char status_msg[]="SyncStatus = %d";
    static const char status_short[]="[ble.ancc]SyncStatus = %d";
    if(audio_log_level()&2u)
        audio_log_extended(4u,module,path,"_rxSyncEventCallback",0x174u,status_msg,status);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,status_short,status_short,status);
    if(status!=0u){
        static const char error[]="!!!!!!!!!!!!!!!Dual-Glasses Communication ERROR = %d!!!!!!!!!!!!!!!";
        static const char error_short[]="[ble.ancc]!!!!!!!!!!!!!!!Dual-Glasses Communication ERROR = %d!!!!!!!!!!!!!!!";
        if(audio_log_level()&2u)
            audio_log_extended(1u,module,path,"_rxSyncEventCallback",0x176u,error,status);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x04400000u,error_short,error_short,status);
    }
    return status;
}
