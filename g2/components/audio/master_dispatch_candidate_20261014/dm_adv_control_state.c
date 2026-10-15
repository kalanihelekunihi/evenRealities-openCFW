#include <stdint.h>

/* Native dmAdvCb RAM 0x20073394. The selected two-handle init and
 * interval paths access bytes through +0x1e; complete span is open. */
uint8_t audio_ble_dm_adv_control[0x20] __attribute__((aligned(4)));
