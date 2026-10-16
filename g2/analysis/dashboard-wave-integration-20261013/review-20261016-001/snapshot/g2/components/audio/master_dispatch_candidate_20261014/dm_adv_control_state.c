#include <stdint.h>

/* Native dmAdvCb RAM 0x20073394. The selected two-handle init and
 * interval paths access through +0x1e. The legacy start action writes a
 * two-byte duration at +0x20; the synthetic connection completion reads
 * peer addresses through +0x30 and address types through +0x32.
 * Complete native allocation and placement remain open. */
uint8_t audio_ble_dm_adv_control[0x34] __attribute__((aligned(4)));
