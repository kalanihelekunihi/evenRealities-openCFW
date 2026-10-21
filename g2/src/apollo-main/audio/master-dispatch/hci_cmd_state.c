#include <stdint.h>

/* Native RAM 0x20073a90: 16-byte WSF timer, eight-byte queue, then
 * command metadata through +0x1a. Native startup values remain open. */
uint8_t audio_ble_hci_cmd_state_20073a90[0x1c] __attribute__((aligned(4)));
