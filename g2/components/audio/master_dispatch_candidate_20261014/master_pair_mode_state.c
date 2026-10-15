#include <stdint.h>

/* Native compressed-SRAM pointer cell 0x20000444. The cell points to
 * mutable mode data; source ownership of that target remains separate. */
volatile uint32_t audio_ble_master_pair_mode_cell_20000444;
