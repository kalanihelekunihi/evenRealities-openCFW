/* SPDX-License-Identifier: Apache-2.0
 * Source projection of Packetcraft Cordio wsf/sources/util/bda.c BdaIsZeros.
 * Pinned upstream commit: 3656312d6b73e2a2c1c8b33ee0385bc199dd97e6.
 * The stock native entry and its full call domain have not been identified.
 */
#include <stdint.h>

uint8_t BdaIsZeros(const uint8_t *address)
{
    uint8_t nonzero = 0;
    for (unsigned i = 0; i < 6u; ++i) {
        nonzero |= address[i];
    }
    return (uint8_t)(nonzero == 0u);
}
