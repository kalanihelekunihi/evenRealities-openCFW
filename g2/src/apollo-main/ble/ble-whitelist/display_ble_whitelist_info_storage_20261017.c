/* Provisional live RAM backing for the ANCC whitelist candidate.
 * Stock base: 0x20054718. The native oracle exercises the first 0x100 bytes;
 * product capacity, initializer, and placement remain separate gates. */
#include <stdint.h>
uint8_t audio_ble_whitelist_info[0x100];
