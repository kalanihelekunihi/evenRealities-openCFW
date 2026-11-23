#include <stdint.h>

/* Native ANCC RAM 0x200695c8..0x20069b23. Reset clears through +0x55b;
 * another native literal references the immediately following address. */
uint8_t audio_ble_ancc_state[0x55c] __attribute__((aligned(4)));

/* Native compressed-RAM ANCC service state 0x200036c8. Stock .data init
 * is 01 01 0a 00 00. C reads [0], [1], [3], [4]; only [4] is written
 * later (whitelist). SVC_ANCC_Init does not set these bytes first. */
uint8_t audio_ble_ancc_service_state[5] = { 1u, 1u, 0x0au, 0u, 0u };
