/* Native HciDrvRadioShutdown 0x4b49ce. */
#include <stdint.h>
extern uint8_t audio_ble_hci_radio_timer[]; /* live WSF timer 0x20073e64 */
extern volatile uint32_t audio_ble_hci_radio_active; /* live 0x20074638 */
extern volatile uint32_t audio_ble_hci_radio_pending; /* live 0x2007463c */
extern volatile uint32_t audio_ble_hci_radio_context_ptr; /* live 0x20074630 */
extern void WsfTimerStop(void *); /* selected 0x52a4d2 */
extern uint32_t audio_ble_hci_radio_disable_52dd6a(void);
extern void audio_ble_hci_radio_switch_52eece(uint8_t);
extern void audio_ble_hci_radio_pins_52dd7c(void);
extern uint32_t audio_ble_hci_radio_reset_52df12(void *);
void audio_ble_hci_driver_radio_shutdown(void) {
    WsfTimerStop(audio_ble_hci_radio_timer);
    (void)audio_ble_hci_radio_disable_52dd6a();
    audio_ble_hci_radio_switch_52eece(0u);
    audio_ble_hci_radio_pins_52dd7c();
    audio_ble_hci_radio_active=0u;
    audio_ble_hci_radio_pending=0u;
    (void)audio_ble_hci_radio_reset_52df12((void *)(uintptr_t)audio_ble_hci_radio_context_ptr);
}
