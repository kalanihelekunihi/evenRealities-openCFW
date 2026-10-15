#include <stdint.h>

/* Native ANCC RAM 0x200695c8..0x20069b23. Reset clears through +0x55b;
 * another native literal references the immediately following address. */
uint8_t audio_ble_ancc_state[0x55c] __attribute__((aligned(4)));

/* Native compressed-RAM ANCC service state 0x200036c8. Current C paths
 * observe bytes 0 and 4; its full native allocation remains unknown. */
uint8_t audio_ble_ancc_service_state[5];
