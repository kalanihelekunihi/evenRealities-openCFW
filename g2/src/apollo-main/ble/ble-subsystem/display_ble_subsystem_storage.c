/* Source-owned mutable Cordio app discovery/advertising state. The selected
 * 0x532e52 reset traverses exactly three 16-byte rows at stock 0x200733fc;
 * 0x4b3c02 clears the 0x80-byte app link state at stock 0x200719c8.
 * Runtime state is produced by those routines and later event handlers;
 * Full-image overlap and initialization remain image-linker obligations. */
#include <stdint.h>
_Alignas(4) uint8_t audio_ble_subsystem_rows_200733fc[3u*0x10u]
    __attribute__((section(".bss.g2.ram.ble_subsystem_rows")));
