/* Native mode selector 0x50938e and watchdog-kick wrapper 0x5118e0.
 * ROM 0x509494/0x5094a4/0x5094a8 -> live bytes 0x20074368/69/6a. */
#include <stdint.h>
extern uint8_t audio_ble_hci_radio_mode_cells_20074368[4];
extern void audio_ble_npmx_kick_watchdog_5118e8(void);

uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t mode) {
    if((uint8_t)mode==1u)return audio_ble_hci_radio_mode_cells_20074368+1u;
    if((uint8_t)mode==2u)return audio_ble_hci_radio_mode_cells_20074368+2u;
    return audio_ble_hci_radio_mode_cells_20074368;
}

/* Stock returns a stale register here (its body is void upstream); no caller reads it. */
uint32_t audio_ble_hci_radio_state_prepare_5118e0(void) {
    audio_ble_npmx_kick_watchdog_5118e8();
    return 0u;
}
