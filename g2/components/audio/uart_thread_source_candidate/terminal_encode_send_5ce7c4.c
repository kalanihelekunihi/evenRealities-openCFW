/* Native Apollo terminal_encode_and_send 0x5ce7c4. */
#include <stdint.h>

struct pb_ostream_candidate {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct pb_ostream_candidate) == 20u, "nanopb ostream ABI");

uint8_t audio_terminal_tx_staging[0x850]
    __attribute__((section(".g2.ram.terminal_tx_staging"),used,aligned(4))); /* RAM 0x200f9694 */
uint8_t audio_terminal_tx_encoded[0x878]
    __attribute__((section(".g2.ram.terminal_tx_encoded"),used,aligned(4))); /* RAM 0x20374378 */
extern const struct pb_msgdesc_candidate audio_terminal_tx_pb_descriptor; /* ROM 0x77c634 */
struct pb_msgdesc_candidate {
    const uint32_t *field_info;
    const struct pb_msgdesc_candidate *const *submsg_info;
    const uint8_t *default_value;
    void *field_callback;
    uint16_t field_count, required_field_count, largest_tag;
};
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void audio_pb_ostream_from_buffer(struct pb_ostream_candidate *, void *, uint32_t);
extern uint32_t audio_pb_encode(struct pb_ostream_candidate *, const void *, const void *);
extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_settings_notify_ble(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.terminal";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[] = "terminal_encode_and_send";
static const char unsupported[] = "unsupported terminal tx tag=%d";
static const char unsupported_short[] = "[pb.terminal]unsupported terminal tx tag=%d";
static const char encode_failed[] = "terminal encode failed: %s";
static const char encode_failed_short[] = "[pb.terminal]terminal encode failed: %s";
static const char none[] = "(none)";

uint32_t audio_terminal_send_message_5ce7c4(uint32_t command, uint32_t tag,
                                              const void *payload,
                                              uint32_t sequence, uint32_t notify) {
    uint8_t *const staging = audio_terminal_tx_staging;
    const uint8_t *const bytes = (const uint8_t *)payload;
    audio_uart_buffer_zero(staging, 0x850u, 0u);
    staging[0] = (uint8_t)command;
    staging[1] = (uint8_t)sequence;
    staging[2] = (uint8_t)tag;
    staging[3] = (uint8_t)(tag >> 8);
    uint32_t size;
    switch ((uint16_t)tag) {
        case 9u: size = 2u; break;
        case 10u: case 12u: case 13u: case 22u: size = 1u; break;
        case 11u: case 18u: case 25u: size = 8u; break;
        case 19u: case 24u: size = 4u; break;
        case 20u: size = 12u; break;
        default:
            if (audio_log_flags() & 2u)
                audio_log_extended(1u, module, path, function, 0x53u,
                                   unsupported, (uint16_t)tag);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compressed_log_output(0x4400000u, unsupported_short,
                                            unsupported_short, (uint16_t)tag);
            return 8u;
    }
    audio_uart_checksum_copy(staging + 4u, bytes, size);
    struct pb_ostream_candidate initialized;
    struct pb_ostream_candidate stream;
    audio_pb_ostream_from_buffer(&initialized, audio_terminal_tx_encoded, 0x878u);
    audio_uart_checksum_copy(&stream, &initialized, 20u);
    if (audio_pb_encode(&stream, &audio_terminal_tx_pb_descriptor, staging) == 0u) {
        const char *why = stream.errmsg != 0 ? stream.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x5au,
                               encode_failed, why);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x4400000u, encode_failed_short,
                                        encode_failed_short, why);
        return 5u;
    }
    if (audio_uart_device_role_get() == 1u) {
        if (notify != 0u)
            (void)audio_settings_notify_ble(1u, 0x30u, audio_terminal_tx_encoded,
                                            (uint16_t)stream.bytes_written);
        else
            (void)audio_ring_pb_tx_ble_475b14(1u, 0x30u, audio_terminal_tx_encoded,
                                              (uint16_t)stream.bytes_written);
    }
    return 0u;
}
