/* Bounded HCI event counters at native Main 0x20073bc0. The selected
 * hciEvtProcessMsg body addresses twelve 16-bit counters (indices 0..11).
 * This object owns those 24 observed bytes; full native allocation extent
 * and absolute SRAM placement remain image-level gates. */
#include <stdint.h>

volatile uint16_t audio_ble_hci_event_counts_20073bc0[12u];
