/*
 * Clean-room re-expression of the first-party standard CRC-32 used by the Even
 * Realities G2 2.2.6.10 protocol layer (transport-protocol packet framing,
 * OTA external-flash verification, and the box-UART manager). The firmware
 * stores the reflected CRC-32 table (polynomial 0xEDB88320) at run 0x006987A8;
 * this file regenerates that table from source and computes the standard
 * reflected CRC-32 (seed 0xFFFFFFFF, final XOR 0xFFFFFFFF), distinct from the
 * already-replaced CRC-32C (efs_crc32c).
 *
 * This is a first-party source-replacement candidate: its generated table is
 * validated byte-for-byte against the firmware table, and its output against
 * the published CRC-32 check value. See docs/research/first-party-frontier-
 * ranking.md.
 */

#include <stdint.h>

static uint32_t even_crc32_byte(uint8_t b)
{
    uint32_t c = b;
    int i;
    for (i = 0; i < 8; i++) {
        c = (c & 1u) ? (c >> 1) ^ 0xEDB88320u : (c >> 1);
    }
    return c;
}

void even_crc32_build_table(uint32_t table[256])
{
    int b;
    for (b = 0; b < 256; b++) {
        table[b] = even_crc32_byte((uint8_t)b);
    }
}

uint32_t even_crc32(const uint8_t *data, uint32_t len)
{
    uint32_t table[256];
    uint32_t crc = 0xFFFFFFFFu;
    uint32_t i;
    even_crc32_build_table(table);
    for (i = 0; i < len; i++) {
        crc = table[(crc ^ data[i]) & 0xFFu] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFFu;
}
