/* QuickList completed-UID nanopb sender at Apollo 0x5591b0..0x559369. */
#include <stdint.h>

struct quicklist_completed_ostream {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct quicklist_completed_ostream) == 20u, "nanopb stream ABI");

extern uint8_t audio_quicklist_tx_packet[0x400];
extern uint8_t audio_quicklist_tx_state[0x1238];
extern const uint8_t audio_quicklist_pb_descriptor[];
extern void audio_pb_ostream_from_buffer(struct quicklist_completed_ostream *, void *, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_pb_encode(void *, const void *, const void *);
extern void audio_ring_pb_tx_ble_475c1a(uint32_t, uint32_t, const void *, uint32_t);
extern void audio_ring_pb_assert_509b48(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.quicklist";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_quicklist\\pb_service_quicklist.c";
static const char function[] = "APP_PbNotifyEncodeQuicklistMultItems";
static const char none[] = "(none)";
static const uint8_t fault_literal[20] = {
    0, 0, 0, 0, 0, 0, 0, 0, 0x58, 0xb3, 0x6d, 0, 0x94, 0xc5, 0x74, 0,
    0x22, 0x01, 0, 0
};

uint32_t audio_quicklist_send_completed_5591b0(uint32_t unused, const void *message) {
    (void)unused;
    if (message == 0) {
        uint8_t fault[20];
        audio_uart_checksum_copy(fault, fault_literal, 20u);
        *(uint16_t *)(void *)(fault + 4u) = 1u;
        audio_ring_pb_assert_509b48(fault);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 292u, "PORINT NULL");
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, "[pb.quicklist]PORINT NULL",
                                        "[pb.quicklist]PORINT NULL");
        return 2u;
    }

    struct quicklist_completed_ostream initial, stream;
    audio_pb_ostream_from_buffer(&initial, audio_quicklist_tx_packet, 0x400u);
    audio_uart_checksum_copy(&stream, &initial, 20u);
    audio_uart_buffer_zero(audio_quicklist_tx_state, 0x1238u, 0u);
    audio_quicklist_tx_state[0] = 2u;
    audio_quicklist_tx_state[1] = *(volatile uint8_t *)(uintptr_t)0x20074ffdu;
    *(volatile uint8_t *)(uintptr_t)0x20074ffdu =
        (uint8_t)(audio_quicklist_tx_state[1] + 1u);
    *(uint16_t *)(void *)(audio_quicklist_tx_state + 2u) = 4u;
    const uint8_t *const input = (const uint8_t *)message;
    audio_quicklist_tx_state[8] = input[0];
    audio_quicklist_tx_state[9] = input[1];
    *(uint16_t *)(void *)(audio_quicklist_tx_state + 10u) =
        *(const uint16_t *)(const void *)(input + 2u);
    const uint32_t count = *(const uint16_t *)(const void *)(input + 2u);
    for (uint32_t index = 0u; index < count; ++index)
        (void)audio_queue_copy_bytes(audio_quicklist_tx_state + 16u + index * 232u,
                                     input + 8u + index * 232u, 232u);

    const uint32_t encoded = (uint8_t)audio_pb_encode(&stream,
                                                     audio_quicklist_pb_descriptor,
                                                     audio_quicklist_tx_state);
    const uint32_t written = (uint16_t)stream.bytes_written;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 317u, "txLen = %d", written);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, "[pb.quicklist]txLen = %d",
                                    "[pb.quicklist]txLen = %d", written);
    if (encoded == 0u) {
        const char *const error = stream.errmsg ? stream.errmsg : none;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 320u,
                               "Encoding failed: %s\n", error);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u,
                                        "[pb.quicklist]Encoding failed: %s\n",
                                        "[pb.quicklist]Encoding failed: %s\n", error);
        return 0x2bu;
    }
    audio_ring_pb_tx_ble_475c1a(1u, 0x0cu, audio_quicklist_tx_packet, written);
    return 0u;
}
