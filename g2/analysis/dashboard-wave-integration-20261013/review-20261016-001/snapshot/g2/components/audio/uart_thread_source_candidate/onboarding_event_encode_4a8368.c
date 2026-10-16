/* Stock APP_PbNotifyEncodeOnboardingEvent, 0x4a8368..0x4a84d2. */
#include <stdint.h>

struct onboarding_ostream {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct onboarding_ostream) == 20u, "nanopb stream ABI");

uint8_t audio_onboarding_event_packet_200f612c[256];
uint8_t audio_onboarding_event_state_200f623c[16];
uint8_t audio_onboarding_event_sequence_20074ffb;

extern const uint8_t audio_onboarding_event_descriptor_779c94[];
extern void audio_pb_ostream_from_buffer(struct onboarding_ostream *, void *, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_pb_encode(void *, const void *, const void *);
extern void audio_ring_pb_tx_ble_475c1a(uint32_t, uint32_t, const void *, uint32_t);
extern void audio_ring_pb_assert_509b48(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.onboarding";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_onboarding\\pb_service_onboarding.c";
static const char function[] = "APP_PbNotifyEncodeOnboardingEvent";
static const char none[] = "(none)";
static const uint8_t fault_literal[20] = {
    0, 0, 0, 0, 0, 0, 0, 0, 0xcc, 0x95, 0x6d, 0,
    0x9c, 0x7b, 0x75, 0, 0x26, 0x01, 0, 0
};

uint32_t audio_onboarding_event_encode_4a8368(uint32_t unused, const void *message)
{
    (void)unused;
    if (message == 0) {
        uint8_t fault[20];
        audio_uart_checksum_copy(fault, fault_literal, sizeof fault);
        *(uint16_t *)(void *)(fault + 4u) = 1u;
        audio_ring_pb_assert_509b48(fault);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x128u, "POINTER NULL");
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, "[pb.onboarding]POINTER NULL",
                                        "[pb.onboarding]POINTER NULL");
        return 2u;
    }

    struct onboarding_ostream initial, stream;
    audio_pb_ostream_from_buffer(&initial, audio_onboarding_event_packet_200f612c, 256u);
    audio_uart_checksum_copy(&stream, &initial, sizeof stream);
    audio_uart_buffer_zero(audio_onboarding_event_state_200f623c, 16u, 0u);
    audio_onboarding_event_state_200f623c[0] = 3u;
    audio_onboarding_event_state_200f623c[1] = audio_onboarding_event_sequence_20074ffb++;
    *(uint16_t *)(void *)(audio_onboarding_event_state_200f623c + 2u) = 5u;
    const uint8_t *input = (const uint8_t *)message;
    audio_onboarding_event_state_200f623c[4] = input[0];
    *(uint32_t *)(void *)(audio_onboarding_event_state_200f623c + 8u) =
        *(const uint32_t *)(const void *)(input + 4u);
    const uint32_t encoded = (uint8_t)audio_pb_encode(&stream,
                                            audio_onboarding_event_descriptor_779c94,
                                            audio_onboarding_event_state_200f623c);
    const uint32_t written = (uint16_t)stream.bytes_written;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x13cu, "txLen = %d", written);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, "[pb.onboarding]txLen = %d",
                                    "[pb.onboarding]txLen = %d", written);
    if (encoded == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x140u,
                               "Encoding failed: %s.", error);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u,
                                        "[pb.onboarding]Encoding failed: %s.",
                                        "[pb.onboarding]Encoding failed: %s.", error);
        return 0x2bu;
    }
    audio_ring_pb_tx_ble_475c1a(1u, 0x10u, audio_onboarding_event_packet_200f612c,
                                  written);
    return 0u;
}
