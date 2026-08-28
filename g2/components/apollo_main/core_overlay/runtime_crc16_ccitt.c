/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room re-expression of the Even Realities G2 2.2.6.10 first-party
 * CRC-16/CCITT computation (polynomial 0x1021, MSB-first, non-reflected). The
 * firmware ships two byte-identical copies of the 256-entry 0x1021 forward
 * table (run 0x006C0350 and 0x006C0B50) and two table-driven update functions
 * that differ only in their seed and length ABI:
 *
 *   - open_cfw_crc16_ccitt_xmodem (stock at run 0x0059D350): seed 0x0000
 *     (CRC-16/XMODEM), signed length. Check value 0x31C3 over "123456789".
 *   - open_cfw_crc16_ccitt (stock at run 0x0049ACD4, 48 callers): seed taken
 *     from a caller pointer, or 0xFFFF when that pointer is null
 *     (CRC-16/CCITT-FALSE, resumable). Check value 0x29B1 over "123456789"
 *     with a null seed.
 *
 * Both tables are the canonical 0x1021 forward table (validated byte-for-byte
 * against a from-polynomial regeneration in
 * tests/test_first_party_crc16_ccitt_leaf.py); these leaves own the update
 * CODE from source while the tables remain pinned official compatibility data,
 * referenced as fixed-address constants exactly as the stock bodies load them.
 * See docs/research/first-party-crc16-ccitt-source-boundary-audit.md.
 */

#include <stdint.h>

#ifndef OPEN_CFW_CRC16_CCITT_XMODEM_TABLE
#define OPEN_CFW_CRC16_CCITT_XMODEM_TABLE ((const uint16_t *)0x006C0350u)
#endif
#ifndef OPEN_CFW_CRC16_CCITT_TABLE
#define OPEN_CFW_CRC16_CCITT_TABLE ((const uint16_t *)0x006C0B50u)
#endif

__attribute__((used, noinline))
uint16_t open_cfw_crc16_ccitt_xmodem(const uint8_t *data, int len)
{
    const uint16_t *table = OPEN_CFW_CRC16_CCITT_XMODEM_TABLE;
    uint16_t crc = 0x0000u;
    int i;

#pragma clang loop unroll(disable)
    for (i = 0; i < len; ++i) {
        crc = (uint16_t)((crc << 8) ^ table[(uint8_t)((crc >> 8) ^ data[i])]);
    }
    return crc;
}

__attribute__((used, noinline))
uint16_t open_cfw_crc16_ccitt(const uint8_t *data, uint32_t len,
                              const uint16_t *seed)
{
    const uint16_t *table = OPEN_CFW_CRC16_CCITT_TABLE;
    uint16_t crc = seed ? *seed : 0xFFFFu;
    uint32_t i;

#pragma clang loop unroll(disable)
    for (i = 0u; i < len; ++i) {
        crc = (uint16_t)((crc << 8) ^ table[(uint8_t)((crc >> 8) ^ data[i])]);
    }
    return crc;
}
