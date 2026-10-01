/* Host parsing interface for the locked G2 v2.2.6.10 ESS audio path.
 * Structural parsing only: cannot certify encoder success or physical validity.
 * The handle is build-specific; discover/map the characteristic on other builds.
 */
#ifndef OPENCFW_ESS_AUDIO_H
#define OPENCFW_ESS_AUDIO_H
#include "../audio-stream-2026-10-01/audio_stream.h"
enum {G2_ESS_VALUE_HANDLE=0x0864,G2_ESS_ATT_BYTES=208,G2_ESS_MIN_MTU=208};
typedef struct {
 const uint8_t *lc3_frames; /* five 40-byte frames only when encoder succeeded */
 uint16_t energy_ratio;    /* integer ratio, not dB; low 16 bits retained */
 int16_t angle_degrees;    /* physical orientation/validity not established */
 uint8_t sequence;
} G2EssAudio;
/* Native app GATT notification callbacks normally supply this 205-byte value. */
static inline bool g2_ess_audio_value(const uint8_t *value,size_t n,G2EssAudio *out) {
 G2AudioBody body;
 if(!out || !g2_audio_body_view(value,n,&body))return false;
 out->lc3_frames=body.lc3;out->energy_ratio=body.metadata0;
 out->angle_degrees=body.metadata1;out->sequence=body.sequence;return true;
}
/* For a reassembled raw ATT PDU from a capture, not an HCI/L2CAP packet. */
static inline bool g2_ess_audio_att(const uint8_t *pdu,size_t n,G2EssAudio *out) {
 if(!pdu || n!=G2_ESS_ATT_BYTES || pdu[0]!=0x1b || pdu[1]!=0x64 || pdu[2]!=0x08)return false;
 return g2_ess_audio_value(pdu+3,n-3,out);
}
#endif
