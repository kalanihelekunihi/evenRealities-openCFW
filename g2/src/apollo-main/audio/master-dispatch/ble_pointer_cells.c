#include <stdint.h>

/* Native profile registration pointer cells in RAM. Runtime initializers
 * populate these; final absolute placement is a separate link gate. */
uint8_t *audio_ble_msgtx_state;                 /* 0x20074338 */
uint8_t *audio_ble_msgtx_mode;                  /* 0x2007433c */
/* 0x2007435c */
/* 0x20074360 */
/* 0x20074364 */

/* RAM 0x20074368..6b: board info {type, hw_version, u16 measured mV} written by board_hw_version_detect_509134; the radio mode selectors read bytes 0..2. */
uint8_t audio_ble_hci_radio_mode_cells_20074368[4];
