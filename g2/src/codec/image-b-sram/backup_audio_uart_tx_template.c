/* Native normal-copy 0x10016f98..0x10016fb7, a mutable 32-byte BUXX
 * packet template consumed by 0x1000b54c and updated by 0x1000c1f8.
 * Every initialized zero below is present in the authenticated stock
 * normal-copy record; runtime fields are subsequently overwritten. */
#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint32_t magic;
    uint16_t command;
    uint8_t sequence;
    uint8_t has_crc;
    uint16_t wire_length;
    uint16_t crc_low;
    uint16_t crc_high;
    uint16_t reserved_header;
    uint32_t payload;
    uint8_t channel;
    uint8_t reserved_channel[3];
    uint32_t payload_length;
    uint32_t reserved_tail;
} image_b_audio_uart_packet;

_Static_assert(sizeof(image_b_audio_uart_packet) == 32, "native packet extent");
_Static_assert(offsetof(image_b_audio_uart_packet, payload) == 0x10,
               "native payload pointer offset");
_Static_assert(offsetof(image_b_audio_uart_packet, channel) == 0x14,
               "native channel offset");
_Static_assert(offsetof(image_b_audio_uart_packet, payload_length) == 0x18,
               "native payload length offset");

volatile image_b_audio_uart_packet gx8002_image_b_audio_uart_tx_20016f98
    __attribute__((section(".data.image_b.audio_uart_tx"), used)) = {
        .magic = UINT32_C(0x58585542), /* BUXX */
        .command = 0u,
        .sequence = 0u,
        .has_crc = 0u,
        .wire_length = 0u,
        .crc_low = 0u,
        .crc_high = 0u,
        .reserved_header = 0u,
        .payload = 0u,
        .channel = 0u,
        .reserved_channel = {0u,0u,0u},
        .payload_length = 0u,
        .reserved_tail = 0u,
    };
