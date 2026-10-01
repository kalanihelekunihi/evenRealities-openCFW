/* Host interpretation helper for the normal G2 source-0 fallback stream BODY.
 * This is not the BLE packet envelope, a codec, or original firmware source.
 * Length 205 does NOT prove successful LC3 encoding; see README failure cases.
 */
#ifndef OPENCFW_AUDIO_STREAM_H
#define OPENCFW_AUDIO_STREAM_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
enum {G2_AUDIO_BODY_BYTES=205,G2_AUDIO_LC3_FRAME_BYTES=40,
      G2_AUDIO_LC3_FRAMES=5,G2_AUDIO_LC3_BYTES=200};
typedef struct {
 const uint8_t *lc3; /* five consecutive 40-byte frames, only on normal success */
 uint16_t metadata0; /* algorithm result; physical meaning/units not verified */
 int16_t metadata1;  /* signed interpretation matches stock diagnostics */
 uint8_t sequence;
} G2AudioBody;
static inline bool g2_audio_body_view(const uint8_t *body,size_t size,G2AudioBody *out) {
 if(!body || !out || size!=G2_AUDIO_BODY_BYTES)return false;
 uint16_t second=(uint16_t)(body[202]|((uint16_t)body[203]<<8));
 out->lc3=body;out->metadata0=(uint16_t)(body[200]|((uint16_t)body[201]<<8));
 out->metadata1=(int16_t)(second<=32767?(int32_t)second:(int32_t)second-65536);
 out->sequence=body[204];return true;
}
/* Modular distance only: gaps can include firmware OTA suppression, not merely
 * missing radio packets. A full wrap/reorder cannot be distinguished here. */
static inline uint8_t g2_audio_sequence_distance(uint8_t previous,uint8_t next) {
 return (uint8_t)(next-previous);
}
#endif
