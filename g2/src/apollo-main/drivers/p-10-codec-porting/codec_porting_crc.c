/* CRC-32 helpers of the GX8002 codec porting layer (service_codec_dfu.c callers
 * at 0x577d7c..0x57a35f), native 0x58faac..0x58fab5 and 0x58fcf0..0x58fd17
 * (literal 0x58fd18 -> table ROM 0x6987a8).
 *
 * codec_dfu_crc32_58faac checks package records with the shared zlib CRC-32
 * (0x4d34c4, seed 0). codec_dfu_crc32_update_58fcf0 is the reflected 0xEDB88320
 * table CRC used for the "serialdown" flash image: the caller supplies the
 * initial value (0xffffffff) and the result is already inverted. */
#include <stdint.h>
#include <stddef.h>

extern const uint32_t g2_codec_crc32_table[256]; /* ROM 0x6987a8, [1] = 0x77073096 */
extern uint32_t crc32_4d34c4(const void *data, uint32_t length, const uint32_t *seed);

uint32_t codec_dfu_crc32_58faac(const void *data, uint32_t length)
{
    return crc32_4d34c4(data, length, NULL);
}

uint32_t codec_dfu_crc32_update_58fcf0(uint32_t crc, uint32_t length, const uint8_t *data)
{
    for (; length != 0u; length--) {
        crc = g2_codec_crc32_table[(uint8_t)(*data ^ (uint8_t)crc)] ^ (crc >> 8);
        data++;
    }
    return crc ^ 0xffffffffu;
}
