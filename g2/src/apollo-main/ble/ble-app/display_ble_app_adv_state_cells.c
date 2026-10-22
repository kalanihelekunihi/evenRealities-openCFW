/* Bounded mutable app advertising cells at native Main 0x20074f92 and
 * 0x20074f94. The pinned state/callback paths read and write one byte at
 * each address. Exact SRAM placement and adjacent object extents remain
 * linker/image obligations. */
#include <stdint.h>

uint8_t audio_ble_adv_transition_pending_20074f94;
