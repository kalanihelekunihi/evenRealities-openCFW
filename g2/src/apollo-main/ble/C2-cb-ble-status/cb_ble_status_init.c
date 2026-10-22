/* BLE_STATUS callback list init/deinit, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\cb_ble_status.c.
 * Native 0x4abcb0..0x4abcc5, written from the 2.2.6.10 disassembly; literal
 * pool 0x4abd70 (ROM 0x78a568 "BLE_STATUS") and 0x4abd74 (RAM 0x20073f6c,
 * the 12-byte callback manager). Register/unregister (0x4abcc6, 0x4abd14)
 * are in ble/ble-status/display_ble_status_callbacks.c, notify in
 * ble/a-19-app-ble/cb_ble_status_notify.c.
 *
 *   0x4abcb0: push {r7,lr}; r1 = "BLE_STATUS"; r0 = manager;
 *             bl CALLBACK_MGR_Init (0x510108); pop {r0,pc}
 *   0x4abcbc: push {r7,lr}; r0 = manager; bl CALLBACK_MGR_Deinit (0x5101ae);
 *             pop {r0,pc}
 * Both discard the callee status. */
#include <stdint.h>

extern uint8_t audio_ble_status_callback_manager[12];          /* RAM 0x20073f6c */
extern uint32_t audio_callback_mgr_init(void *manager, const char *name); /* CALLBACK_MGR_Init 0x510108 */
extern uint32_t CALLBACK_MGR_Deinit(void *manager);            /* 0x5101ae */

static const char ble_status_name[] = "BLE_STATUS";            /* ROM 0x78a568 */

void cb_ble_status_init_4abcb0(void);
void cb_ble_status_deinit_4abcbc(void);

/* Stock 0x4ABCB0 */
void cb_ble_status_init_4abcb0(void) {
    (void)audio_callback_mgr_init(audio_ble_status_callback_manager, ble_status_name);
}

/* Stock 0x4ABCBC */
void cb_ble_status_deinit_4abcbc(void) {
    (void)CALLBACK_MGR_Deinit(audio_ble_status_callback_manager);
}
