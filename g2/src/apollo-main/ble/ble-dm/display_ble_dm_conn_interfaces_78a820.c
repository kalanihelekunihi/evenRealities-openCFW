/* Three Cordio dmFcnIf_t records at stock Apollo Main 0x78a820..0x78a843.
 * The order follows the registered Cordio dm_conn.c interface definitions.
 * Child functions remain separate C source obligations. */
#include <stdint.h>

typedef void (*dm_interface_entry_t)(void);
extern void audio_ble_dm_conn_reset_4b67ec(void);
extern void audio_ble_dm_conn_hci_handler_4b68a4(void);
extern void audio_ble_dm_conn_msg_handler_4b6888(void);
extern void audio_ble_dm_empty_reset_4d29be(void);
extern void audio_ble_dm_conn2_hci_handler_4b6990(void);
extern void audio_ble_dm_conn2_msg_handler_4b6914(void);
extern void audio_ble_dm_empty_handler_4d29c0(void);
extern void audio_ble_dm_conn_upd_msg_handler_4b6a16(void);

__attribute__((used))
const dm_interface_entry_t audio_ble_dm_conn_table_a[3] = {
    audio_ble_dm_conn_reset_4b67ec,
    audio_ble_dm_conn_hci_handler_4b68a4,
    audio_ble_dm_conn_msg_handler_4b6888,
};
__attribute__((used))
const dm_interface_entry_t audio_ble_dm_conn_table_b[3] = {
    audio_ble_dm_empty_reset_4d29be,
    audio_ble_dm_conn2_hci_handler_4b6990,
    audio_ble_dm_conn2_msg_handler_4b6914,
};
__attribute__((used))
const dm_interface_entry_t audio_ble_dm_conn_table_c[3] = {
    audio_ble_dm_empty_reset_4d29be,
    audio_ble_dm_empty_handler_4d29c0,
    audio_ble_dm_conn_upd_msg_handler_4b6a16,
};
