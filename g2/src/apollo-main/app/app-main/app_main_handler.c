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

__attribute__((naked))
uint32_t audio_ble_app_reset_callback_4bda34(void){
    __asm__ volatile(
        "push {r7, lr}\n"
        "ldr r1, =audio_ble_ui_callback_cells\n"
        "ldr r0, [r1, #8]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldr r0, [r1, #8]\n"
        "blx r0\n"
        "1: pop {r0, pc}\n");
}


