/* Bounded HCI error callback and last-code cells at native Main
 * 0x20074644 and 0x20074648. The native compared error path reads/writes
 * these as 32-bit values; placement and callback target remain open. */
#include <stdint.h>

uint32_t audio_ble_hci_error_callback_20074644;
volatile uint32_t audio_ble_hci_error_value_20074648;
