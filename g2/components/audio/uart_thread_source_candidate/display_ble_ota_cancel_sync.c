/* Native OTA cancel 0x448784 and RPC status sync 0x444e90. */
#include <stdint.h>

extern uint8_t audio_ble_ota_export_state[]; /* live 0x20072730 */
extern volatile uint8_t audio_ble_ota_sync_enabled; /* live 0x20074ff3 */
extern volatile uint8_t audio_ble_ota_sync_status; /* live 0x20075024 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern int32_t audio_ble_send_status_message(uint32_t,const uint8_t *,uint32_t,uint32_t); /* selected 0x464d1c */

static const char module[]="ota.service";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ota_service\\ota_service.c";
static const char name[]="_RPC_SystemOtaStatusSync";
static const char format[]="RPC_SystemOtaStatusSync state = %d";
static const char compact[]="[ota.service]RPC_SystemOtaStatusSync state = %d";

void audio_ble_rpc_ota_status_sync(uint32_t status) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,name,0x332u,format,status&0xffu);
    uint32_t flags=audio_log_flags();
    if((flags&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,compact,compact,status&0xffu);
    if(audio_ble_ota_sync_enabled==0u) {
        uint8_t packet[8]={1u,0u,1u,0u,0u,0u,0u,0u};
        packet[4]=audio_ble_ota_sync_status;
        packet[5]=audio_ble_ota_sync_status==1u?2u:1u;
        packet[6]=(uint8_t)status;
        (void)audio_ble_send_status_message(0x103u,packet,8u,0u);
    }
}

void audio_ble_ota_disconnect(void) {
    audio_uart_buffer_zero(audio_ble_ota_export_state,0x60u,0u);
    audio_ble_ota_export_state[0]=0u;
    uint32_t resume_pointer=0x2034bc10u; /* authenticated literal at 0x44887c */
    __builtin_memcpy(audio_ble_ota_export_state+0x34u,&resume_pointer,4u);
    audio_ble_rpc_ota_status_sync(0u);
}
