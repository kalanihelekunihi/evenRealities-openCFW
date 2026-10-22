/* Native 0x4487ac, 0x46f258, and 0x46f1d0. */
#include <stdint.h>
extern uint8_t *audio_ble_slave_connection_info; /* pointer cell RAM 0x20074330 */
extern volatile uint8_t audio_ota_transfer_flag; /* RAM 0x20072730 */
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern uint32_t audio_ota_self_status(void); /* native UX_GetSelfOTAStatus */
extern uint32_t audio_ota_peer_status(void); /* native UX_GetPeerOTAStatus */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.Slave";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c";
static const char cmd_function[]="APP_IsLocalSlaveAsCmdRole";
static const char left_function[]="APP_IsLeftSlaveRole";
static const char cmd_message[]="pEvenSlaveConnInfo->cmdPipe = %d(%d)";
static const char cmd_short[]="[ble.Slave]pEvenSlaveConnInfo->cmdPipe = %d(%d)";
static const char left_message[]="pEvenSlaveConnInfo->cmdPipe = %d(%d)(LEFT = 2|RIGHT = 1)";
static const char left_short[]="[ble.Slave]pEvenSlaveConnInfo->cmdPipe = %d(%d)(LEFT = 2|RIGHT = 1)";
/* Stock 0x004487AC (semantic_OtaTransferActive) */
uint32_t audio_ota_transfer_active(void) {
    if(audio_ota_self_status()==1u||audio_ota_peer_status()==1u) return 1u;
    return audio_ota_transfer_flag==1u;
}
/* Stock 0x0046F258 (APP_IsLeftSlaveRole) */
uint32_t audio_app_is_left_slave_role(void) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,left_function,795u,left_message,
                           audio_ble_slave_connection_info[31u],audio_uart_device_role_get());
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,left_short,left_short,
                                    audio_ble_slave_connection_info[31u],audio_uart_device_role_get());
    return audio_uart_device_role_get()==2u;
}
/* Stock 0x0046F1D0 (APP_IsLocalSlaveAsCmdRole) */
uint32_t audio_app_is_local_slave_cmd_role(void) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,cmd_function,788u,cmd_message,
                           audio_ble_slave_connection_info[31u],audio_uart_device_role_get());
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,cmd_short,cmd_short,
                                    audio_ble_slave_connection_info[31u],audio_uart_device_role_get());
    return audio_uart_device_role_get()==1u||audio_ble_slave_connection_info[31u]==0u;
}
