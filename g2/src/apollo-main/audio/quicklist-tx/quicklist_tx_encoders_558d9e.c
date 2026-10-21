/* QuickList APP_PbTxEncode{Item,MultItems,Event} at 0x558d9e,
 * 0x558ffe, and 0x559470. Native TX state and packet are product BSS. */
#include <stdint.h>

struct quicklist_pb_ostream {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct quicklist_pb_ostream) == 20u, "nanopb ostream ABI");

extern const uint8_t audio_quicklist_pb_descriptor[];
extern void audio_pb_ostream_from_buffer(struct quicklist_pb_ostream *, void *, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_pb_encode(void *, const void *, const void *);
extern void audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t, const void *, uint32_t);
extern void audio_ring_pb_assert_509b48(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

uint8_t audio_quicklist_tx_packet[0x400];
uint8_t audio_quicklist_tx_state[0x1238];

static const char module[] = "pb.quicklist";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_quicklist\\pb_service_quicklist.c";
static const char none[] = "(none)";
static const uint8_t item_fault[20] = {
    0,0,0,0,0,0,0,0,0x58,0xb3,0x6d,0,0x94,0xf9,0x76,0,0xa5,0,0,0};
static const uint8_t many_fault[20] = {
    0,0,0,0,0,0,0,0,0x58,0xb3,0x6d,0,0x28,0x7d,0x75,0,0xfe,0,0,0};
static const uint8_t event_fault[20] = {
    0,0,0,0,0,0,0,0,0x58,0xb3,0x6d,0,0x90,0x36,0x76,0,0x58,1,0,0};

static uint32_t encode(uint32_t command, uint8_t id, const uint8_t *payload,
                       const char *function, const uint8_t fault_literal[20],
                       uint32_t null_line, uint32_t length_line, uint32_t error_line) {
    if (payload == 0) {
        uint8_t fault[20];
        audio_uart_checksum_copy(fault, fault_literal, 20u);
        fault[4] = 1u;
        fault[5] = 0u;
        audio_ring_pb_assert_509b48(fault);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, null_line, "PORINT NULL");
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, "[pb.quicklist]PORINT NULL",
                                        "[pb.quicklist]PORINT NULL");
        return 2u;
    }
    struct quicklist_pb_ostream initial, stream;
    audio_pb_ostream_from_buffer(&initial, audio_quicklist_tx_packet, 0x400u);
    audio_uart_checksum_copy(&stream, &initial, 20u);
    audio_uart_buffer_zero(audio_quicklist_tx_state, 0x1238u, 0u);
    audio_quicklist_tx_state[0] = (uint8_t)command;
    audio_quicklist_tx_state[1] = id;
    audio_quicklist_tx_state[2] = (uint8_t)(command + 2u);
    if (command == 1u) {
        for (uint32_t i = 0; i < 12u; ++i) audio_quicklist_tx_state[8u+i] = payload[i];
        audio_quicklist_tx_state[0xecu] = 0u;
    } else if (command == 2u) {
        audio_quicklist_tx_state[8] = payload[0];
        audio_quicklist_tx_state[9] = payload[1];
        audio_quicklist_tx_state[0x1230u] = 0u;
    } else {
        audio_quicklist_tx_state[8] = payload[0];
        for (uint32_t i = 0; i < 4u; ++i) audio_quicklist_tx_state[12u+i] = payload[4u+i];
        audio_quicklist_tx_state[16] = 0u;
    }
    uint32_t encoded = (uint8_t)audio_pb_encode(&stream, audio_quicklist_pb_descriptor,
                                                 audio_quicklist_tx_state);
    uint32_t written = (uint16_t)stream.bytes_written;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, length_line,
                           "txLen = %d", written);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, "[pb.quicklist]txLen = %d",
                                    "[pb.quicklist]txLen = %d", written);
    if (encoded == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, error_line,
                               "Encoding failed: %s\n", error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u,
                                        "[pb.quicklist]Encoding failed: %s\n",
                                        "[pb.quicklist]Encoding failed: %s\n", error);
        return 0x2bu;
    }
    audio_ring_pb_tx_ble_475b14(1u, 0x0cu, audio_quicklist_tx_packet, written);
    return 0u;
}

uint32_t audio_quicklist_one_dispatch(uint32_t id, const void *payload) {
    return encode(1u, (uint8_t)id, payload, "APP_PbTxEncodeQuicklistItem",
                  item_fault, 0xa7u, 0xbdu, 0xc0u);
}
uint32_t audio_quicklist_many_dispatch(uint32_t id, const void *payload) {
    return encode(2u, (uint8_t)id, payload, "APP_PbTxEncodeQuicklistMultItems",
                  many_fault, 0x100u, 0x115u, 0x118u);
}
uint32_t audio_quicklist_event_dispatch(uint32_t id, const void *payload) {
    return encode(3u, (uint8_t)id, payload, "APP_PbTxEncodeQuicklistEvent",
                  event_fault, 0x15au, 0x16fu, 0x172u);
}
