/* APP_PbConversateTxEncodeTagTrackingData, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_conversate\pb_service_conversate.c.
 * Native 0x5b212e..0x5b223b (literal pool shared with 0x5b200e at 0x5b2244..0x5b22b8).
 *
 * Builds the 0xa3 "tag tracking" Conversate frame (12-byte payload copied from
 * the tag page's tracking record: tag_id, open_type, close_type, duration_ms),
 * nanopb-encodes it with the shared Conversate descriptor and, on the glasses
 * master side (device role 1), notifies it over BLE as PB service 0x0b.
 * Returns 0 ok, 5 encode error, 6 NULL argument. */
#include <stdint.h>
#include <stddef.h>
#include "conversate_ui_context.h" /* g2_conversate_tag_tracking_t (UI context +0xa0) */

typedef struct {
    void *callback;      /* +0x00 */
    void *state;         /* +0x04 */
    uint32_t max_size;   /* +0x08 */
    uint32_t bytes_written; /* +0x0c */
    const char *errmsg;  /* +0x10 */
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "nanopb ostream");


extern uint8_t audio_conversate_response_frame_200f4808[4012];   /* RAM 0x200f4808 */
extern uint8_t audio_conversate_response_encoded_2037c2a0[256];  /* RAM 0x2037c2a0 */
extern uint8_t audio_conversate_last_magic_20074ff8;             /* RAM 0x20074ff8 */
extern const uint8_t audio_conversate_response_descriptor_775b24[]; /* ROM 0x775b24 pb_msgdesc_t */

extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size); /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);         /* 0x490c32 */
extern uint32_t display_driver_uled_mode_45a568(void);  /* device role, 1 = master */
extern uint32_t Thread_MsgPbNotifyByBle(uint8_t type, uint8_t command, const void *payload,
                                        uint16_t length); /* 0x475c1a */

static const char module[] = "pb.conversate"; /* ROM 0x787d00 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_conversate\\pb_service_conversate.c"; /* ROM 0x6d942c */
static const char function[] = "APP_PbConversateTxEncodeTagTrackingData"; /* ROM 0x74c184 */
static const char null_message[] = "pTagTrackingData is NULL"; /* ROM 0x76f4a8 */
static const char null_short[] = "[pb.conversate]pTagTrackingData is NULL"; /* ROM 0x74c1ac */
static const char encode_message[] = "Encoding failed: %s"; /* ROM 0x781908 */
static const char encode_short[] = "[pb.conversate]Encoding failed: %s"; /* ROM 0x7576f8 */
static const char none[] = "(none)"; /* ROM 0x78de84 */

uint32_t APP_PbConversateTxEncodeTagTrackingData(const g2_conversate_tag_tracking_t *tracking)
{
    if (tracking == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0xefu, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, null_short, null_short);
        return 6u;
    }

    uint8_t *const frame = audio_conversate_response_frame_200f4808;
    aeabi_memset_43c0e4(frame, sizeof(audio_conversate_response_frame_200f4808), 0);
    frame[0] = 0xa3u;                                       /* tag tracking frame */
    frame[1] = (uint8_t)(audio_conversate_last_magic_20074ff8 + 1u);
    *(uint16_t *)(void *)(frame + 2) = 12u;                 /* payload length */
    *(g2_conversate_tag_tracking_t *)(void *)(frame + 4) = *tracking;

    g2_pb_ostream_t stream, out;
    audio_pb_ostream_from_buffer(&stream, audio_conversate_response_encoded_2037c2a0, 256u);
    aeabi_memcpy4_439c04(&out, &stream, sizeof(out));
    if ((uint8_t)audio_pb_encode(&out, audio_conversate_response_descriptor_775b24, frame) == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0xfcu, encode_message,
                               out.errmsg != NULL ? out.errmsg : none);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04400000u, encode_short, encode_short,
                                      out.errmsg != NULL ? out.errmsg : none);
        return 5u;
    }
    if (display_driver_uled_mode_45a568() == 1u)
        (void)Thread_MsgPbNotifyByBle(1u, 0x0bu, audio_conversate_response_encoded_2037c2a0,
                                      (uint16_t)out.bytes_written);
    return 0u;
}
