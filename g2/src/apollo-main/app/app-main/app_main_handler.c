/* Native Packetcraft AppHandler 0x4bae84 and app event children
 * 0x4bacc8/0x4bda34. Callback cells are live, registered app state. */
#include <stdint.h>
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern uint32_t (*audio_ble_subsystem_primary_callback_slot)(const uint8_t *); /* live 0x200740fc */
extern uint32_t (*audio_ble_subsystem_callback_slot)(const uint8_t *); /* live 0x20074100 */
extern uintptr_t audio_ble_ui_callback_cells[]; /* live 0x20073f60, reset callback at +8 */
extern void DmReadRemoteFeatures(uint8_t); /* native 0x4b6cb0 */

/* Stock returns a stale register here (its body is void upstream); no caller reads it. */
uint32_t audio_ble_app_reset_callback_4bda34(void){
    void (*reset)(void)=(void (*)(void))audio_ble_ui_callback_cells[2];
    if(reset!=0)reset();
    return 0u;
}


