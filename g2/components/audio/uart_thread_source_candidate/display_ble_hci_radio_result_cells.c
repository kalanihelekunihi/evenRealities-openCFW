/* Bounded mutable HCI radio result words at native Main 0x20074224 and
 * 0x20074228. The acquire, context-check, and simple query candidates
 * address each as a 32-bit cell. Exact SRAM placement is still open. */
#include <stdint.h>

volatile uint32_t audio_ble_hci_radio_revision_word_20074224;
volatile uint32_t audio_ble_hci_radio_detect_word_20074228;
