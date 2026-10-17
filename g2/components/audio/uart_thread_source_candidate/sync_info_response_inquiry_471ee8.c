/* Native SyncInfoService_response_inquiry_cmd at 0x471ee8..0x471fa3.
 * Descriptor and formatter remain separately owned source dependencies. */
#include <stdint.h>

struct sync_info_ostream {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct sync_info_ostream) == 20u, "nanopb ostream ABI");

extern uint8_t audio_sync_info_response_200740c8[12];
extern uint8_t audio_sync_info_encode_buffer_20071c48[128];
extern const uint8_t audio_sync_info_pb_descriptor_77c1cc[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_get_running_app_ids(uint32_t *, uint32_t *);
extern void audio_pb_ostream_from_buffer(struct sync_info_ostream *, void *, uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern uint32_t audio_pb_encode(struct sync_info_ostream *, const void *, const void *);
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "sync_info.main";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\sync_info\\sync_info.c";
static const char function[] = "syncInfoService_response_inquiry_cmd";
static const char failed[] = "syncInfoService: pb_encode failed";
static const char short_failed[] = "[sync_info.main]syncInfoService: pb_encode failed";

uint32_t audio_sync_info_command_471ee8(uint32_t inquiry) {
    audio_uart_buffer_zero(audio_sync_info_response_200740c8, 12u, 0u);
    audio_uart_buffer_zero(audio_sync_info_encode_buffer_20071c48, 128u, 0u);
    audio_sync_info_response_200740c8[0] = 0u;
    audio_sync_info_response_200740c8[1] = (uint8_t)inquiry;
    uint32_t background, foreground;
    (void)audio_get_running_app_ids(&background, &foreground);
    audio_sync_info_response_200740c8[2] = 1u;
    for (unsigned i = 0; i < 4; ++i) {
        audio_sync_info_response_200740c8[4u+i] = (uint8_t)(background >> (i*8u));
        audio_sync_info_response_200740c8[8u+i] = (uint8_t)(foreground >> (i*8u));
    }
    struct sync_info_ostream stream, encoded;
    audio_pb_ostream_from_buffer(&stream, audio_sync_info_encode_buffer_20071c48, 128u);
    (void)audio_uart_display_area_copy_439c04(&encoded, &stream, 20u);
    if (audio_pb_encode(&encoded, audio_sync_info_pb_descriptor_77c1cc,
                        audio_sync_info_response_200740c8) == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 60u, failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, short_failed, short_failed);
        return 0u;
    }
    uint32_t result = audio_ring_pb_tx_ble_475b14(1u, 13u,
                              audio_sync_info_encode_buffer_20071c48,
                              (uint16_t)encoded.bytes_written);
    /* The native empty loop counts to bytes_written when BLE send returns 0. */
    return result ? result : encoded.bytes_written;
}
