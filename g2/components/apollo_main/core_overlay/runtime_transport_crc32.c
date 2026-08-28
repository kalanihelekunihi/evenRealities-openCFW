/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room re-expression of the Even Realities G2 2.2.6.10 first-party
 * transport CRC-32 finaliser at run 0x0058FCF0 (the standard reflected CRC-32,
 * polynomial 0xEDB88320). The stock function walks a caller-seeded CRC across a
 * byte buffer using the precomputed reflected table at run 0x006987A8 and
 * returns the finalised value. It backs transport-protocol packet framing, OTA
 * external-flash verification, and the box-UART manager.
 *
 * ABI recovered by focused disassembly of the 40-byte stock body: r0 = seed
 * CRC, r1 = length, r2 = data pointer; returns (table-updated CRC) ^
 * 0xFFFFFFFF. The sole caller at run 0x00579856 seeds r0 = 0xFFFFFFFF, so
 * open_cfw_transport_crc32_update(0xFFFFFFFF, len, data) is the canonical
 * CRC-32 (check value 0xCBF43926 over "123456789").
 *
 * The stored table at 0x006987A8 is the canonical reflected CRC-32 table,
 * validated byte-for-byte against a from-polynomial regeneration (see
 * research/candidates/first_party_crc32.c and
 * docs/research/first-party-transport-crc32-source-boundary-audit.md). This
 * leaf owns the update CODE from source; the table remains pinned official
 * compatibility data, referenced as a fixed-address constant just as the stock
 * body loads it from its literal pool.
 */

#include <stdint.h>

/*
 * The target leaf loads the stored table from its fixed run address, exactly as
 * the stock body does. A host equivalence test overrides this to point at a
 * copy of the same firmware table (see
 * tests/test_first_party_transport_crc32_leaf.py), which is why the address is a
 * single overridable definition rather than an inline literal.
 */
#ifndef OPEN_CFW_TRANSPORT_CRC32_TABLE
#define OPEN_CFW_TRANSPORT_CRC32_TABLE ((const uint32_t *)0x006987A8u)
#endif

__attribute__((used, noinline))
uint32_t open_cfw_transport_crc32_update(
    uint32_t crc,
    uint32_t len,
    const uint8_t *data
)
{
    const uint32_t *table = OPEN_CFW_TRANSPORT_CRC32_TABLE;

#pragma clang loop unroll(disable)
    while (len != 0u) {
        crc = table[(uint8_t)(crc ^ *data)] ^ (crc >> 8);
        ++data;
        --len;
    }
    return crc ^ 0xFFFFFFFFu;
}
