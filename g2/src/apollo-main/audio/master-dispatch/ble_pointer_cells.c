#include <stdint.h>

/* Native profile registration pointer cells in RAM. Runtime initializers
 * populate these; final absolute placement is a separate link gate. */
uint8_t *audio_ble_msgtx_state;                 /* 0x20074338 */
uint8_t *audio_ble_msgtx_mode;                  /* 0x2007433c */
const uint8_t *audio_ble_msgtx_table_slot;     /* 0x2007435c */
const void *audio_ble_profile_dispatch_slot;  /* 0x20074360 */
const void *audio_ble_profile_table_slot;     /* 0x20074364 */

/* Native radio mode selectors at RAM 0x20074368..6a. */
uint8_t audio_ble_hci_radio_mode_cells_20074368[3];
