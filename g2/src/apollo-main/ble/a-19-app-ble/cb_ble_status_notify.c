/* BLE status callback fan-out, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\cb_ble_status.c.
 * Native CB_BLE_STATUS_Notify 0x4abd60..0x4abd6d; literal pool 0x4abd74.
 * Register/unregister (0x4abcc6, 0x4abd14) live in ble/ble-status and own the
 * manager object. */
#include <stdint.h>

extern uint8_t audio_ble_status_callback_manager[12]; /* RAM 0x20073f6c */
extern void audio_even_ai_ancc_display_send_5105bc(void *manager, uint32_t event,
                                                   const uint32_t *value); /* CALLBACK_MGR_Notify 0x5105bc */

/* Callbacks receive (event, &value); the value lives in the caller's frame. */
void CB_BLE_STATUS_Notify(uint32_t event, uint32_t value)
{
    audio_even_ai_ancc_display_send_5105bc(audio_ble_status_callback_manager, event, &value);
}
