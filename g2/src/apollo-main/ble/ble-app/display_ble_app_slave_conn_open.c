/* Product connection-open selector native Main 0x46de78, authenticated
 * event layout, live pointer cells and diagnostic literals. */
#include <stdint.h>
extern uint8_t *audio_ble_dm_conn_cell; /* RAM pointer cell 0x20074328 */
extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern uint8_t *audio_ble_profile_connection_context; /* RAM pointer cell 0x2007432c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
void appSlaveConnOpen(void *message)
{
    static const char module[]="ble.Slave";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c";
    static const char function[]="_bleSlaveGetCB";
    static const char format[]="ble_connect = 0x%x";
    static const char compact[]="[ble.Slave]ble_connect = 0x%x";
    const uint8_t *const event=(const uint8_t *)message;
    uint16_t connection=(uint16_t)event[0u]|((uint16_t)event[1u]<<8u);
    audio_ble_dm_conn_cell=audio_ble_discovery_connection_records_200717b0+
                           ((uint32_t)connection-1u)*0x30u;
    audio_ble_profile_connection_context[0x54u]=(uint8_t)connection;
    if (audio_log_flags()&2u)
        audio_log_extended(4u,module,source,function,0x129u,format,audio_ble_dm_conn_cell);
    if ((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,compact,compact,audio_ble_dm_conn_cell);
}
