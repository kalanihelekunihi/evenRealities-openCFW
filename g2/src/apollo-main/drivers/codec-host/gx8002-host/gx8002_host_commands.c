/* GX8002 host request functions, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_codec_host.c.
 * Native 0x57baf4..0x57bb09 and 0x57c664..0x57d3af, 0x57da40..0x57db57;
 * literal pools 0x57c610..0x57c63f, 0x57d004.., 0x57db64..0x57dc3f.
 *
 * Every request uses up to three attempts. An attempt zeroes the 26-byte
 * message, sends with family 0x100 and waits for the answer through
 * gx8002_send_and_wait_response (which opens and closes UART3 itself); a
 * failed attempt logs and frees the message. The response is not matched
 * against the request command or sequence. Return 0 ok, -1 bad argument or
 * short response, otherwise the transport/unpack status of the last try. */
#include <stdint.h>
#include <stddef.h>
#include "gx8002_host.h"

extern uint8_t g2_gx8002_version[4];            /* RAM 0x20074940, last version read */
extern uint8_t g2_audio_transaction_transport[]; /* RAM 0x2007397c, 30-byte RX scratch */
extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t length);        /* 0x4751c8 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t length); /* 0x439c04 */
extern int32_t audio_uart_send_bytes(const void *wire, uint32_t count); /* 0x58fb38, UART ch3 TX */

static const char module[] = "codec.host"; /* ROM 0x78bed0 */
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c"; /* ROM 0x6fccd4 */

static const char magic_word[4] = {'B', 'U', 'X', 'X'}; /* ROM 0x78f3b8 */

/* Pre-built 0x010e request: seq 1, no body, header CRC 0x682fdbd4. Sixteen
 * bytes are copied to the stack, fourteen are sent. */
static const uint8_t mic_delay_frame[16] = {
    0x42, 0x55, 0x58, 0x58, 0x0e, 0x01, 0x01, 0x00,
    0x00, 0x00, 0xd4, 0xdb, 0x2f, 0x68, 0x00, 0x00,
}; /* ROM 0x7888a0 */

static const char fn_read_version[] = "GX8002_ReadVersion"; /* ROM 0x783064 */
static const char read_version_attempt[] = "ReadVersion attempt %d failed: %d"; /* ROM 0x759708 */
static const char read_version_attempt_s[] = "[codec.host]ReadVersion attempt %d failed: %d"; /* ROM 0x7380e4 */
static const char read_version_length[] = "Invalid version response length: %d"; /* ROM 0x75972c */
static const char read_version_length_s[] = "[codec.host]Invalid version response length: %d"; /* ROM 0x738114 */
static const char read_version_ok[] = "Version: %d.%d.%d.%d"; /* ROM 0x77b65c */
static const char read_version_ok_s[] = "[codec.host]Version: %d.%d.%d.%d"; /* ROM 0x759750 */

static const char fn_bf[] = "GX8002_SwitchBFMode"; /* ROM 0x783078 */
static const char bf_attempt[] = "SwitchBFMode attempt %d failed: %d"; /* ROM 0x759774 */
static const char bf_attempt_s[] = "[codec.host]SwitchBFMode attempt %d failed: %d"; /* ROM 0x738144 */
static const char bf_length[] = "Invalid BF mode response length: %d"; /* ROM 0x759798 */
static const char bf_length_s[] = "[codec.host]Invalid BF mode response length: %d"; /* ROM 0x738174 */
static const char bf_ok[] = "BF mode switch status: 0x%02X"; /* ROM 0x764c70 */
static const char bf_ok_s[] = "[codec.host]BF mode switch status: 0x%02X"; /* ROM 0x742f6c */

static const char fn_wakeup[] = "GX8002_SwitchWakeupMode"; /* ROM 0x77b674 */
static const char wakeup_attempt[] = "SwitchWakeupMode attempt %d failed: %d"; /* ROM 0x74db4c */
static const char wakeup_attempt_s[] = "[codec.host]SwitchWakeupMode attempt %d failed: %d"; /* ROM 0x72d144 */
static const char wakeup_length[] = "Invalid wakeup mode response length: %d"; /* ROM 0x74db74 */
static const char wakeup_length_s[] = "[codec.host]Invalid wakeup mode response length: %d"; /* ROM 0x72d178 */
static const char wakeup_ok[] = "Wakeup mode switch status: 0x%02X"; /* ROM 0x7597bc */
static const char wakeup_ok_s[] = "[codec.host]Wakeup mode switch status: 0x%02X"; /* ROM 0x7381a4 */

static const char fn_mic_state[] = "GX8002_QueryMicState"; /* ROM 0x77b68c */
static const char mic_state_attempt[] = "QueryMicState attempt %d failed: %d"; /* ROM 0x7597e0 */
static const char mic_state_attempt_s[] = "[codec.host]QueryMicState attempt %d failed: %d"; /* ROM 0x7381d4 */
static const char mic_state_length[] = "Invalid mic state response length: %d"; /* ROM 0x74db9c */
static const char mic_state_length_s[] = "[codec.host]Invalid mic state response length: %d"; /* ROM 0x72d1ac */
static const char mic_state_ok[] = "Mic state query status: 0x%04X"; /* ROM 0x764c90 */
static const char mic_state_ok_s[] = "[codec.host]Mic state query status: 0x%04X"; /* ROM 0x742f98 */

static const char fn_gain[] = "GX8002_SetMicGain"; /* ROM 0x78308c */
static const char gain_attempt[] = "SetMicGain attempt %d failed: %d"; /* ROM 0x759804 */
static const char gain_attempt_s[] = "[codec.host]SetMicGain attempt %d failed: %d"; /* ROM 0x738204 */
static const char gain_length[] = "Invalid mic gain response length: %d"; /* ROM 0x74dbc4 */
static const char gain_length_s[] = "[codec.host]Invalid mic gain response length: %d"; /* ROM 0x72d1e0 */
static const char gain_ok[] = "SetMicGain status: 0x%04X"; /* ROM 0x77108c */
static const char gain_ok_s[] = "[codec.host]SetMicGain status: 0x%04X"; /* ROM 0x74dbec */

static const char fn_delay[] = "GX8002_MicDelay1Bit"; /* ROM 0x7830a0 */
static const char delay_send[] = "Failed to send UART data: %d"; /* ROM 0x764c10 */
static const char delay_send_s[] = "[codec.host]Failed to send UART data: %d"; /* ROM 0x742f14 */
static const char delay_read[] = "Failed to read response: %d"; /* ROM 0x7710c4 */
static const char delay_read_s[] = "[codec.host]Failed to read response: %d"; /* ROM 0x74dc64 */
static const char delay_attempt[] = "MicDelay1Bit attempt %d failed: %d"; /* ROM 0x75984c */
static const char delay_attempt_s[] = "[codec.host]MicDelay1Bit attempt %d failed: %d"; /* ROM 0x738264 */
static const char delay_length[] = "Invalid mic delay 1bit response length: %d"; /* ROM 0x743048 */
static const char delay_length_s[] = "[codec.host]Invalid mic delay 1bit response length: %d"; /* ROM 0x722a50 */
static const char delay_ok[] = "Mic delay 1bit status: 0x%02X"; /* ROM 0x764cf0 */
static const char delay_ok_s[] = "[codec.host]Mic delay 1bit status: 0x%02X"; /* ROM 0x743074 */

static const char fn_voice[] = "GX8002_GetVoiceEvent"; /* ROM 0x77b704 */
static const char voice_attempt[] = "GetVoiceEvent: unpack message attempt %d failed: %d"; /* ROM 0x72d2b0 */
static const char voice_attempt_s[] = "[codec.host]GetVoiceEvent: unpack message attempt %d failed: %d"; /* ROM 0x70eb64 */
static const char voice_ok[] = "voice event: cmd_id=0x%04X, event_id=0x%04X"; /* ROM 0x7430cc */
static const char voice_ok_s[] = "[codec.host]voice event: cmd_id=0x%04X, event_id=0x%04X"; /* ROM 0x722af8 */

static uint16_t body_u16(const g2_gx8002_message_t *msg)
{
    const uint8_t *body = msg->body;
    return (uint16_t)((uint32_t)body[0] | ((uint32_t)body[1] << 8));
}

/* 0x57baf4: memcmp against "BUXX"; 0 means the magic matches. No callers
 * found; the unpacker compares the bytes inline. */
int32_t semantic_gx8002_magic_matches(const void *frame)
{
    char expected[4];
    expected[0] = magic_word[0];
    expected[1] = magic_word[1];
    expected[2] = magic_word[2];
    expected[3] = magic_word[3];
    return g2_lfs_memcmp(frame, expected, 4u);
}

/* 0x57c664: cmd 0x0102, response 0x0202 with 4 bytes; also cached in RAM. */
int32_t GX8002_ReadVersion(uint8_t version[4], uint32_t timeout)
{
    g2_gx8002_message_t msg;
    int32_t status;

    if (version == NULL)
        return -1;
    status = -1;
    for (int32_t attempt = 0; attempt < GX8002_ATTEMPTS; attempt++) {
        audio_uart_buffer_zero(&msg, sizeof msg, 0u);
        status = audio_send_transaction(GX8002_CMD_READ_VERSION, GX8002_FAMILY_REQUEST,
                                        NULL, 0u, 0u, &msg, timeout);
        if (status == 0)
            break;
        GX8002_LOG(2u, 0x08800000u, fn_read_version, 382u, read_version_attempt,
                   read_version_attempt_s, attempt + 1, status);
        audio_release_transaction(&msg);
    }
    if (status != 0)
        return status;
    if (msg.body_length < 4u) {
        GX8002_LOG(1u, 0x04400000u, fn_read_version, 401u, read_version_length,
                   read_version_length_s, msg.body_length);
        audio_release_transaction(&msg);
        return -1;
    }
    version[0] = msg.body[0];
    version[1] = msg.body[1];
    version[2] = msg.body[2];
    version[3] = msg.body[3];
    g2_gx8002_version[0] = version[0];
    g2_gx8002_version[1] = version[1];
    g2_gx8002_version[2] = version[2];
    g2_gx8002_version[3] = version[3];
    GX8002_LOG(4u, 0x11000000u, fn_read_version, 406u, read_version_ok, read_version_ok_s,
               version[0], version[1], version[2], version[3]);
    audio_release_transaction(&msg);
    return 0;
}

/* 0x57c830: cmd 0x0107. The codec answers 0x0207 status 1, then reboots into
 * its other (beamforming) firmware slot. *status = first body byte. */
int32_t GX8002_SwitchBFMode(uint8_t *status_out, uint32_t timeout)
{
    g2_gx8002_message_t msg;
    int32_t status;

    if (status_out == NULL)
        return -1;
    status = -1;
    for (int32_t attempt = 0; attempt < GX8002_ATTEMPTS; attempt++) {
        audio_uart_buffer_zero(&msg, sizeof msg, 0u);
        status = audio_send_transaction(GX8002_CMD_SWITCH_BF_MODE, GX8002_FAMILY_REQUEST,
                                        NULL, 0u, 0u, &msg, timeout);
        if (status == 0)
            break;
        GX8002_LOG(2u, 0x08800000u, fn_bf, 428u, bf_attempt, bf_attempt_s, attempt + 1, status);
        audio_release_transaction(&msg);
    }
    if (status != 0)
        return status;
    if (msg.body_length == 0u) {
        GX8002_LOG(1u, 0x04400000u, fn_bf, 439u, bf_length, bf_length_s, msg.body_length);
        audio_release_transaction(&msg);
        return -1;
    }
    *status_out = msg.body[0];
    GX8002_LOG(4u, 0x10400000u, fn_bf, 444u, bf_ok, bf_ok_s, *status_out);
    audio_release_transaction(&msg);
    return 0;
}

/* 0x57c9b8: cmd 0x0108. The codec answers 0x0208 status 0 (not 1), then
 * toggles its boot slot back to the wakeup (keyword) firmware. */
int32_t GX8002_SwitchWakeupMode(uint8_t *status_out, uint32_t timeout)
{
    g2_gx8002_message_t msg;
    int32_t status;

    if (status_out == NULL)
        return -1;
    status = -1;
    for (int32_t attempt = 0; attempt < GX8002_ATTEMPTS; attempt++) {
        audio_uart_buffer_zero(&msg, sizeof msg, 0u);
        status = audio_send_transaction(GX8002_CMD_SWITCH_WAKEUP_MODE, GX8002_FAMILY_REQUEST,
                                        NULL, 0u, 0u, &msg, timeout);
        if (status == 0)
            break;
        GX8002_LOG(2u, 0x08800000u, fn_wakeup, 466u, wakeup_attempt, wakeup_attempt_s,
                   attempt + 1, status);
        audio_release_transaction(&msg);
    }
    if (status != 0)
        return status;
    if (msg.body_length == 0u) {
        GX8002_LOG(1u, 0x04400000u, fn_wakeup, 477u, wakeup_length, wakeup_length_s,
                   msg.body_length);
        audio_release_transaction(&msg);
        return -1;
    }
    *status_out = msg.body[0];
    GX8002_LOG(4u, 0x10400000u, fn_wakeup, 482u, wakeup_ok, wakeup_ok_s, *status_out);
    audio_release_transaction(&msg);
    return 0;
}

/* 0x57cb60: cmd 0x0170, response 0x0270 with u16 mic/VAD state. */
int32_t GX8002_QueryMicState(uint16_t *state, uint32_t timeout)
{
    g2_gx8002_message_t msg;
    int32_t status;

    if (state == NULL)
        return -1;
    status = -1;
    for (int32_t attempt = 0; attempt < GX8002_ATTEMPTS; attempt++) {
        audio_uart_buffer_zero(&msg, sizeof msg, 0u);
        status = audio_send_transaction(GX8002_CMD_QUERY_MIC_STATE, GX8002_FAMILY_REQUEST,
                                        NULL, 0u, 0u, &msg, timeout);
        if (status == 0)
            break;
        GX8002_LOG(2u, 0x08800000u, fn_mic_state, 542u, mic_state_attempt,
                   mic_state_attempt_s, attempt + 1, status);
        audio_release_transaction(&msg);
    }
    if (status != 0)
        return status;
    if (msg.body_length < 2u) {
        GX8002_LOG(1u, 0x04400000u, fn_mic_state, 552u, mic_state_length,
                   mic_state_length_s, msg.body_length);
        audio_release_transaction(&msg);
        return -1;
    }
    *state = body_u16(&msg);
    GX8002_LOG(4u, 0x10400000u, fn_mic_state, 556u, mic_state_ok, mic_state_ok_s, *state);
    audio_release_transaction(&msg);
    return 0;
}

/* 0x57ccec: cmd 0x010b with a 1-byte PGA gain (codec accepts 0..48),
 * response 0x020b with u16 status, 1 = accepted. */
int32_t GX8002_SetMicGain(uint8_t gain, uint16_t *status_out, uint32_t timeout)
{
    g2_gx8002_message_t msg;
    int32_t status;

    if (status_out == NULL)
        return -1;
    status = -1;
    for (int32_t attempt = 0; attempt < GX8002_ATTEMPTS; attempt++) {
        audio_uart_buffer_zero(&msg, sizeof msg, 0u);
        status = audio_send_transaction(GX8002_CMD_SET_MIC_GAIN, GX8002_FAMILY_REQUEST,
                                        &gain, 1u, 0u, &msg, timeout);
        if (status == 0)
            break;
        GX8002_LOG(2u, 0x08800000u, fn_gain, 578u, gain_attempt, gain_attempt_s,
                   attempt + 1, status);
        audio_release_transaction(&msg);
    }
    if (status != 0)
        return status;
    if (msg.body_length < 2u) {
        GX8002_LOG(1u, 0x04400000u, fn_gain, 588u, gain_length, gain_length_s,
                   msg.body_length);
        audio_release_transaction(&msg);
        return -1;
    }
    *status_out = body_u16(&msg);
    GX8002_LOG(4u, 0x10400000u, fn_gain, 593u, gain_ok, gain_ok_s, *status_out);
    audio_release_transaction(&msg);
    return 0;
}

/* 0x57d1cc: sends the fixed 0x010e frame directly instead of packing one
 * (the shared sequence counter is not used), then reads and unpacks the
 * answer by hand. A failed send or read closes UART3 without freeing; a
 * failed unpack frees. The codec answers 0x010e with one byte, 1. */
int32_t GX8002_MicDelay1Bit(uint8_t *status_out, uint32_t timeout)
{
    g2_gx8002_message_t msg;
    uint8_t frame[16];
    uint16_t received;
    int32_t status;

    if (status_out == NULL)
        return -1;
    status = -1;
    for (int32_t attempt = 0; attempt < GX8002_ATTEMPTS; attempt++) {
        audio_uart_buffer_zero(&msg, sizeof msg, 0u);
        (void)audio_transaction_init();
        audio_uart_checksum_copy(frame, mic_delay_frame, 16u);
        status = audio_uart_send_bytes(frame, (uint16_t)14u);
        if (status != 0) {
            GX8002_LOG(1u, 0x04400000u, fn_delay, 703u, delay_send, delay_send_s, status);
            audio_transaction_cleanup();
            continue;
        }
        received = 0u;
        status = audio_transaction_exchange(g2_audio_transaction_transport,
                                            GX8002_RX_CAPACITY, &received, timeout);
        if (status != 0) {
            GX8002_LOG(1u, 0x04400000u, fn_delay, 712u, delay_read, delay_read_s, status);
            audio_transaction_cleanup();
            continue;
        }
        audio_transaction_cleanup();
        status = audio_transaction_extract(g2_audio_transaction_transport, received, &msg);
        if (status == 0)
            break;
        GX8002_LOG(2u, 0x08800000u, fn_delay, 725u, delay_attempt, delay_attempt_s,
                   attempt + 1, status);
        audio_release_transaction(&msg);
    }
    if (status != 0)
        return status;
    if (msg.body_length == 0u) {
        GX8002_LOG(1u, 0x04400000u, fn_delay, 737u, delay_length, delay_length_s,
                   msg.body_length);
        audio_release_transaction(&msg);
        return -1;
    }
    *status_out = msg.body[0];
    GX8002_LOG(4u, 0x10400000u, fn_delay, 742u, delay_ok, delay_ok_s, *status_out);
    audio_release_transaction(&msg);
    return 0;
}

/* 0x57da40: receive-only. Reads one asynchronous 0x03xx event frame with a
 * fixed 200-tick timeout; the caller has already opened UART3 and closes it.
 * A read failure retries silently, an unpack failure logs and frees.
 * event->id is the frame TYPE byte, event->value the first two body bytes
 * (no body-length check). */
int32_t GX8002_GetVoiceEvent(g2_gx8002_voice_event_t *event)
{
    g2_gx8002_message_t msg;
    uint16_t received;
    int32_t status;

    if (event == NULL)
        return -1;
    status = -1;
    for (int32_t attempt = 0; attempt < GX8002_ATTEMPTS; attempt++) {
        audio_uart_buffer_zero(&msg, sizeof msg, 0u);
        received = 0u;
        status = audio_transaction_exchange(g2_audio_transaction_transport,
                                            GX8002_RX_CAPACITY, &received, 200u);
        if (status != 0)
            continue;
        status = audio_transaction_extract(g2_audio_transaction_transport, received, &msg);
        if (status == 0)
            break;
        GX8002_LOG(1u, 0x04800000u, fn_voice, 890u, voice_attempt, voice_attempt_s,
                   attempt + 1, status);
        audio_release_transaction(&msg);
    }
    if (status != 0)
        return status;
    event->id = msg.type;
    event->value = body_u16(&msg);
    GX8002_LOG(2u, 0x08800000u, fn_voice, 900u, voice_ok, voice_ok_s, event->id,
               event->value);
    audio_release_transaction(&msg);
    return 0;
}
