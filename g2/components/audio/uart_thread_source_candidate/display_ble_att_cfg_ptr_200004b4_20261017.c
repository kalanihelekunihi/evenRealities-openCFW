/* Mutable ATT configuration pointer cell at stock RAM 0x200004b4.
 * Stock startup record 0x433104 initializes it to RAM 0x20000414.
 * Final linker placement and overlap with startup scatter remain open. */
#include <stdint.h>

uint32_t audio_ble_att_cfg_ptr_200004b4 = 0x20000414u;
