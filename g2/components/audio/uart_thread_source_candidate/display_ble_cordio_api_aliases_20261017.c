/* Cordio-facing entry points for previously stock-oracled Main providers. */
#include <stdint.h>

extern uint16_t audio_ble_dm_conn_check_idle_4b73a2(uint8_t connection);
extern uint16_t audio_ble_hci_max_rx_acl_len_530d4c(void);

uint16_t DmConnCheckIdle(uint8_t connection)
{
    return audio_ble_dm_conn_check_idle_4b73a2(connection);
}

uint16_t HciGetMaxRxAclLen(void)
{
    return audio_ble_hci_max_rx_acl_len_530d4c();
}
