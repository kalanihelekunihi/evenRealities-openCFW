/* Stock UX_GetPeerRingStatus, 0x47d8f0..0x47d8fc. */
#include <stdint.h>

extern volatile uint8_t audio_ota_packed_status;

uint32_t audio_ble_peer_ring_status_47d8f0(void)
{
    return ((uint32_t)audio_ota_packed_status & 0x3fu) >> 5u;
}
