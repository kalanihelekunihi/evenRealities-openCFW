/* Native BLE logger packet handler 0x5bf972..0x5bf9f6. */
#include <stdint.h>

struct pb_ostream_candidate {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct pb_ostream_candidate) == 20u,
               "nanopb ostream ABI");

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_pb_ostream_from_buffer(struct pb_ostream_candidate *,
                                        void *, uint32_t);
extern uint32_t audio_pb_encode(struct pb_ostream_candidate *, const void *,
                                const void *);
extern uint32_t audio_ring_pb_tx_ble_475c1a(uint32_t, uint32_t,
                                             const void *, uint32_t);
extern const uint8_t audio_uart_ble_log_pb_descriptor_777da4[];

uint8_t audio_uart_ble_log_frame_20069b24[0x508u]
    __attribute__((section(".bss.audio_uart_ble_log_frame"), used));
uint8_t audio_uart_ble_log_encoded_2037cba0[0xc8u]
    __attribute__((section(".bss.audio_uart_ble_log_encoded"), used));

uint32_t audio_uart_logger_ble_handler_5bf972(const uint8_t *message,
                                                uint32_t length) {
    uint8_t *const frame = audio_uart_ble_log_frame_20069b24;
    audio_uart_buffer_zero(frame, 0x508u, 0u);
    frame[0] = 3u;
    frame[1] = 0u;
    frame[2] = 5u;
    frame[3] = 0u;
    const uint32_t copy_length = length < 0x80u ? length : 0x80u;
    for (uint32_t index = 0; index < copy_length; ++index)
        frame[4u + index] = message[index];
    frame[4u + copy_length] = 0u;

    struct pb_ostream_candidate stream;
    audio_pb_ostream_from_buffer(&stream, audio_uart_ble_log_encoded_2037cba0,
                                 0xc8u);
    if (audio_pb_encode(&stream, audio_uart_ble_log_pb_descriptor_777da4,
                        frame) == 0u)
        return 0u;
    (void)audio_ring_pb_tx_ble_475c1a(1u, 0x0fu,
                                       audio_uart_ble_log_encoded_2037cba0,
                                       (uint16_t)stream.bytes_written);
    return length;
}
