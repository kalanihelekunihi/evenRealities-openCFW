/* APP_PbRxQuicklistFrameDataProcess, native 0x55894c. */
#include <stdint.h>

struct quicklist_pb_stream {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct quicklist_pb_stream) == 16u, "nanopb stream ABI");

extern uint8_t audio_quicklist_rx_state[0x1238];
extern const uint8_t audio_quicklist_pb_descriptor[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_pb_stream_init(struct quicklist_pb_stream *, const void *, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern uint32_t audio_uart_pb_decode(void *, const void *, void *);
extern uint32_t audio_quicklist_one_validate(uint32_t, const void *);
extern uint32_t audio_quicklist_one_dispatch(uint32_t, const void *);
extern uint32_t audio_quicklist_many_validate(uint32_t, const void *);
extern uint32_t audio_quicklist_many_dispatch(uint32_t, const void *);
extern uint32_t audio_quicklist_event_validate(uint32_t, const void *);
extern uint32_t audio_quicklist_event_dispatch(uint32_t, const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.quicklist";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_quicklist\\pb_service_quicklist.c";
static const char function[] = "APP_PbRxQuicklistFrameDataProcess";
static const char none[] = "(none)";

uint32_t audio_quicklist_frame_process_55894c(const void *data, uint16_t length) {
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x2eu, "len=%d", length);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, "[pb.quicklist]len=%d",
                                    "[pb.quicklist]len=%d", length);
    if (data == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x30u, "pData is NULL");
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, "[pb.quicklist]pData is NULL",
                                        "[pb.quicklist]pData is NULL");
        return 2u;
    }
    audio_uart_buffer_zero(audio_quicklist_rx_state, 0x1238u, 0u);
    struct quicklist_pb_stream initial, stream;
    audio_uart_pb_stream_init(&initial, data, length);
    audio_uart_checksum_copy(&stream, &initial, 16u);
    if ((uint8_t)audio_uart_pb_decode(&stream, audio_quicklist_pb_descriptor,
                                      audio_quicklist_rx_state) == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x3au,
                               "Decoding failed: %s", error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u,
                                        "[pb.quicklist]Decoding failed: %s",
                                        "[pb.quicklist]Decoding failed: %s", error);
        return 0x2bu;
    }
    uint32_t command = audio_quicklist_rx_state[0];
    uint32_t id = audio_quicklist_rx_state[1];
    const void *payload = audio_quicklist_rx_state + 8u;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x3eu,
                           "quicklist command_id: %d", command);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u,
                                    "[pb.quicklist]quicklist command_id: %d",
                                    "[pb.quicklist]quicklist command_id: %d", command);
    if (command == 1u) {
        if (audio_quicklist_one_validate(id, payload) == 0u)
            return audio_quicklist_one_dispatch(id, payload);
    } else if (command == 2u) {
        if (audio_quicklist_many_validate(id, payload) == 0u)
            return audio_quicklist_many_dispatch(id, payload);
    } else if (command == 3u) {
        if (audio_quicklist_event_validate(id, payload) == 0u)
            return audio_quicklist_event_dispatch(id, payload);
    }
    return 1u;
}
