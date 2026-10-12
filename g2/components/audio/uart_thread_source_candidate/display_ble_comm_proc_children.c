/* Native connected children 0x4bb07c and 0x4b82e8. */
#include <stdint.h>
extern uint8_t audio_ble_atts_connection_rows[]; /* live RAM 0x200717b0 */
extern const uint8_t audio_ble_comm_profile_table[]; /* immutable ROM 0x78c9a4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern int32_t audio_ble_send_status_message(uint32_t,const uint8_t *,uint32_t,uint32_t); /* selected 0x464d1c */
uint8_t *audio_ble_pair_record(uint8_t conn) {
    /* Native table uses connId-1 and 0x30-byte records, including connId zero. */
    const uint8_t *slot=(const uint8_t *)((uintptr_t)audio_ble_atts_connection_rows+
      (uint32_t)conn*0x30u-0x30u);
    uint32_t value=(uint32_t)slot[0]|((uint32_t)slot[1]<<8)|
      ((uint32_t)slot[2]<<16)|((uint32_t)slot[3]<<24);
    return (uint8_t *)(uintptr_t)value;
}
void audio_ble_slave_security_state(uint8_t state) {
    static const char module[]="ble.comm";
    static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble.c";
    static const char function[]="RPC_SystemBleStatusSync";
    static const char message[]="RPC_SystemBleStatusSync state = %d";
    static const char short_message[]="[ble.comm]RPC_SystemBleStatusSync state = %d";
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,path,function,0x3b8u,message,state);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,short_message,short_message,state);
    uint8_t payload[8];
    for(uint32_t i=0u;i<8u;i++)payload[i]=audio_ble_comm_profile_table[8u+i];
    payload[4u]=audio_uart_device_role_get();
    payload[5u]=audio_uart_device_role_get()==1u?2u:1u;
    payload[6u]=state;
    (void)audio_ble_send_status_message(0x103u,payload,8u,0u);
}
