/* Native SyncInfoService_Notify 0x471fa4..0x472101. */
#include <stdint.h>

struct sync_info_ostream {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct sync_info_ostream) == 20u, "nanopb ostream ABI");

extern void *codec_allocate(uint32_t);
extern void audio_file_heap_free(void *);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_get_running_app_ids(uint32_t *, uint32_t *);
extern void audio_pb_ostream_from_buffer(struct sync_info_ostream *, void *, uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern uint32_t audio_pb_encode(struct sync_info_ostream *, const void *, const void *);
extern const uint8_t audio_sync_info_pb_descriptor_77c1cc[];
extern uint32_t audio_settings_notify_ble(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "sync_info.main";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\sync_info\\sync_info.c";
static const char function[] = "syncInfoService_Notify";
static const char nav_failed[] = "syncInfoService  malloc failed for nav_msg_ptr";
static const char nav_short[] =
    "[sync_info.main]syncInfoService  malloc failed for nav_msg_ptr";
static const char buf_failed[] = "syncInfoService: malloc failed for resp_buf_ptr";
static const char buf_short[] =
    "[sync_info.main]syncInfoService: malloc failed for resp_buf_ptr";
static const char encode_failed[] = "syncInfoService: pb_encode failed";
static const char encode_short[] =
    "[sync_info.main]syncInfoService: pb_encode failed";

static void log_failure(uint32_t line, const char *message,
                        const char *short_message) {
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x04000000u, short_message, short_message);
}

/* Stock 0x471FA4 (sync_info_fn_00471fa4) */
uint32_t audio_uart_display_sync_info(void) {
    uint8_t *message = (uint8_t *)codec_allocate(12u);
    if (!message) {
        log_failure(81u, nav_failed, nav_short);
        return UINT32_MAX;
    }
    uint8_t *buffer = (uint8_t *)codec_allocate(128u);
    if (!buffer) {
        log_failure(88u, buf_failed, buf_short);
        audio_file_heap_free(message);
        return UINT32_MAX;
    }
    audio_uart_buffer_zero(message, 12u, 0u);
    audio_uart_buffer_zero(buffer, 128u, 0u);
    message[0] = 1u;
    message[1] = 0u;
    uint32_t background, foreground;
    (void)audio_get_running_app_ids(&background, &foreground);
    message[2] = 1u;
    for (unsigned i = 0; i < 4; ++i) {
        message[4u+i] = (uint8_t)(background >> (i*8u));
        message[8u+i] = (uint8_t)(foreground >> (i*8u));
    }
    struct sync_info_ostream stream, encoded;
    audio_pb_ostream_from_buffer(&stream, buffer, 128u);
    (void)audio_uart_display_area_copy_439c04(&encoded, &stream, 20u);
    uint32_t result;
    if (!audio_pb_encode(&encoded, audio_sync_info_pb_descriptor_77c1cc,
                         message)) {
        log_failure(107u, encode_failed, encode_short);
        result = 0u;
    } else {
        result = audio_settings_notify_ble(1u, 13u, buffer,
                                           (uint16_t)encoded.bytes_written);
    }
    audio_file_heap_free(message);
    audio_file_heap_free(buffer);
    return result;
}
