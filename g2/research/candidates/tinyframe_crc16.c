/*
 * Clean-room source-equivalent of the Even Realities G2 2.2.6.10 TinyFrame
 * TF_CKSUM_CRC16 checksum, recovered by focused disassembly and documented in
 * docs/research/tinyframe-wire-format-recovery-audit.md:
 *
 *   TF_CksumStart @0x0049172C : returns 0x0000 (seed)
 *   TF_CksumAdd   @0x00491730 : crc = table[(crc ^ byte) & 0xFF] ^ (crc >> 8)
 *   TF_CksumEnd   @0x0049174E : identity (no final XOR, no reflect-out)
 *
 * The static table is CRC-16/ARC (polynomial 0x8005, reflected 0xA001), and is
 * the same table the firmware stores at run address 0x006C0950. TinyFrame is
 * MIT-licensed; this file is a clean-room re-expression of the recovered
 * configuration, not copied firmware bytes. It exists to prove the recovered
 * checksum is exactly reproducible from human-readable source under the
 * Linux (linux-clang) toolchain.
 */

#include <stdint.h>

typedef uint16_t tf_cksum_t;

/*
 * Reflected CRC-16/ARC single-byte step starting from a zero CRC. Building the
 * 256-entry table this way reproduces the firmware's static table exactly,
 * without embedding any copied table bytes.
 */
static tf_cksum_t tf_crc16_byte(uint8_t b)
{
    tf_cksum_t crc = b;
    int i;
    for (i = 0; i < 8; i++) {
        crc = (crc & 1u) ? (tf_cksum_t)((crc >> 1) ^ 0xA001u)
                         : (tf_cksum_t)(crc >> 1);
    }
    return crc;
}

void tf_crc16_build_table(tf_cksum_t table[256])
{
    int b;
    for (b = 0; b < 256; b++) {
        table[b] = tf_crc16_byte((uint8_t)b);
    }
}

tf_cksum_t tf_cksum_start(void)
{
    return 0x0000u;
}

tf_cksum_t tf_cksum_add(const tf_cksum_t *table, tf_cksum_t crc, uint8_t byte)
{
    return (tf_cksum_t)(table[(crc ^ byte) & 0xFFu] ^ (crc >> 8));
}

tf_cksum_t tf_cksum_end(tf_cksum_t crc)
{
    return crc;
}

/* Full-buffer CRC using the recovered start/add/end contract. */
tf_cksum_t tf_crc16(const uint8_t *data, uint32_t len)
{
    tf_cksum_t table[256];
    tf_cksum_t crc;
    uint32_t i;
    tf_crc16_build_table(table);
    crc = tf_cksum_start();
    for (i = 0; i < len; i++) {
        crc = tf_cksum_add(table, crc, data[i]);
    }
    return tf_cksum_end(crc);
}
