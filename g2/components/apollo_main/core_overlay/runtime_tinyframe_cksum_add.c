/*
 * Source-owned replacement for the Even Realities G2 2.2.6.10 TinyFrame
 * TF_CksumAdd checksum step (stock at run 0x00491730, 30 bytes), recovered in
 * docs/research/tinyframe-wire-format-recovery-audit.md and validated in
 * research/candidates/tinyframe_crc16.c.
 *
 * The stock function computes crc = table[(crc ^ byte) & 0xFF] ^ (crc >> 8)
 * against a static CRC-16/ARC table at run 0x006C0950. This re-expression is a
 * table-free CRC-16/ARC single-byte update: behaviourally identical for every
 * (crc, byte) input, but self-contained so it appends as a relocation-free
 * overlay leaf without co-placing the rodata table. `optnone` keeps it a
 * portable loop; at -O2 the compiler would otherwise re-materialise the table
 * (and its data relocation), which the append-only leaf format does not carry.
 *
 * TinyFrame is MIT-licensed; this is a clean-room re-expression of the recovered
 * configuration, not copied firmware bytes.
 */

#include <stdint.h>

__attribute__((optnone))
uint16_t open_cfw_tinyframe_cksum_add(uint16_t crc, uint8_t byte)
{
    unsigned c = (unsigned)(crc ^ byte);
    int i;
    for (i = 0; i < 8; i++) {
        c = (c >> 1) ^ (0xA001u & (unsigned)(-(int)(c & 1u)));
    }
    return (uint16_t)c;
}
