/* Bounded HCI reset random retry counter at native Main 0x20074fd0.
 * The selected reset sequence clears and increments this one-byte cell.
 * Absolute SRAM placement and boot initialization remain image gates. */
#include <stdint.h>

volatile uint8_t audio_ble_hci_reset_rand_count;
