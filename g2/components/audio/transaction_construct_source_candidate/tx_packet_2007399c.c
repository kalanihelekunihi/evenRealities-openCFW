/* GX8002 TX scratch starts at stock Main RAM 0x2007399c. The normal
 * constructor accepts a declared body at most 16 bytes plus 14-byte header.
 * A uint16_t length-wrap input can violate that intended bound and remains
 * an explicit separate correctness gate. */
#include <stdint.h>

__attribute__((used, section(".g2_tx_packet_2007399c"), aligned(4)))
uint8_t g2_audio_tx_packet[30];

_Static_assert(sizeof g2_audio_tx_packet == 30u, "GX8002 nominal TX size");
