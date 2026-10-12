/* Native radio revision/detect/enable 0x52dee6/0x52deee/0x52dd58.
 * ROM slots 0x52ea24/0x52eaec point to live 0x20074224/0x20074228. */
#include <stdint.h>
extern volatile uint32_t audio_ble_hci_radio_revision_word_20074224;
extern volatile uint32_t audio_ble_hci_radio_detect_word_20074228;
extern const uint8_t audio_ble_hci_radio_detect_log_768ac8[];
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern void audio_ble_hci_radio_pin_mask_4810b0(uint32_t,uint32_t,uint32_t *);

uint32_t audio_ble_hci_radio_revision_52dee6(void) {
    return audio_ble_hci_radio_revision_word_20074224;
}
uint32_t audio_ble_hci_radio_detect_52deee(void) {
    uint32_t word=audio_ble_hci_radio_detect_word_20074228;
    audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_detect_log_768ac8,word);
    return audio_ble_hci_radio_detect_word_20074228==0x0301ff04u;
}
uint32_t audio_ble_hci_radio_enable_52dd58(void) {
    uint32_t mode=0x75u;
    audio_ble_hci_radio_pin_mask_4810b0(0u,1u,&mode);
    return mode;
}
