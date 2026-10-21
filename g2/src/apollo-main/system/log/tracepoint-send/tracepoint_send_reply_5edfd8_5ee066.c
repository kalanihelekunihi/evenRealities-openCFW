/* Stock Main 0x5edfd8 and 0x5ee066: encoded tracepoint reply transports. */
#include <stdint.h>

extern uint32_t audio_tracepoint_encode_response_5eded0(const uint8_t *, uint16_t *);
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t, const uint8_t *, uint32_t);
extern uint32_t audio_settings_send_peer_packet(uint32_t, const uint8_t *,
                                                         uint32_t, uint32_t, uint32_t);
extern uint8_t audio_tracepoint_encoded_buffer[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "tp.setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char phone_fn[] = "tracepoint_send_to_phone";
static const char master_fn[] = "tracepoint_send_to_master";
static const char phone_msg[] = "tracepoint send to phone cmd=%d len=%u ret=%d";
static const char phone_short[] = "[tp.setting]tracepoint send to phone cmd=%d len=%u ret=%d";
static const char master_msg[] = "tracepoint send to master event=%u cmd=%d len=%u ret=%d";
static const char master_short[] = "[tp.setting]tracepoint send to master event=%u cmd=%d len=%u ret=%d";

uint32_t audio_tracepoint_send_to_phone_5edfd8(const uint8_t *reply)
{
    uint16_t length = 0;
    uint32_t result;
    if (audio_tracepoint_encode_response_5eded0(reply, &length) != 0u)
        return UINT32_MAX;
    result = audio_ring_pb_tx_ble_475b14(1u, 0x11u, audio_tracepoint_encoded_buffer, length);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, phone_fn, 0xf9u, phone_msg,
                           reply[0], length, result);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10c00000u, phone_short, phone_short,
                                    reply[0], length, result);
    return result;
}

uint32_t audio_tracepoint_send_to_master_5ee066(uint32_t event, const uint8_t *reply)
{
    uint16_t length = 0;
    uint32_t result;
    if (audio_tracepoint_encode_response_5eded0(reply, &length) != 0u)
        return UINT32_MAX;
    result = audio_settings_send_peer_packet(0x11u,
                audio_tracepoint_encoded_buffer, length, 0u, (uint16_t)event);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, master_fn, 0x108u, master_msg,
                           (uint16_t)event, reply[0], length, result);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x11000000u, master_short, master_short,
                                    (uint16_t)event, reply[0], length, result);
    return result;
}
