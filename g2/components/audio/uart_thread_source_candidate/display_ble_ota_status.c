/* Native UX_GetSelfOTAStatus/UX_GetPeerOTAStatus 0x47d8b8/0x47d8c2. */
#include <stdint.h>
extern volatile uint8_t audio_ota_packed_status; /* RAM 0x20075043 */
uint32_t audio_ota_self_status(void) {return audio_ota_packed_status&1u;}
uint32_t audio_ota_peer_status(void) {return (audio_ota_packed_status&3u)>>1u;}
