/* Provisional source storage for the two stock Case reconnect state bytes.
 * Stock _BoxDetect_TryReconnectRing 0x4ac19c references these exact cells.
 * Final RAM section placement and startup initialization remain separate gates.
 */
#include <stdint.h>

volatile uint8_t audio_box_reconnect_suppressed_20075010
    __attribute__((section(".g2_ram_20075010"), used));
volatile uint8_t audio_box_reconnect_pending_20075011
    __attribute__((section(".g2_ram_20075011"), used));
