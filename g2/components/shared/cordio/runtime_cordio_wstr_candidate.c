/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * The two definitions are equivalent to the Apache-2.0 Packetcraft Cordio
 * implementations retained from r19.02 through r20.05c.  Ambiq's proprietary
 * copy is used only as a source-family identity oracle.
 */

#include "runtime_cordio_wstr_candidate.h"

#if !defined(OPEN_CFW_WSTR_REVERSE_COPY_ONLY) && \
    !defined(OPEN_CFW_WSTR_REVERSE_ONLY)
#define OPEN_CFW_WSTR_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_WSTR_BUILD_ALL) || \
    defined(OPEN_CFW_WSTR_REVERSE_COPY_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wstr_reverse_copy_candidate(
    uint8_t *destination,
    const uint8_t *source,
    uint16_t length
)
{
    int16_t index;

    for (index = 0; index < length; index++) {
        destination[length - 1 - index] = source[index];
    }
}
#endif

#if defined(OPEN_CFW_WSTR_BUILD_ALL) || \
    defined(OPEN_CFW_WSTR_REVERSE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_wstr_reverse_candidate(uint8_t *buffer, uint8_t length)
{
    uint8_t index;
    uint8_t temporary;

    for (index = 0; index < length / 2U; index++) {
        temporary = buffer[length - index - 1U];
        buffer[length - index - 1U] = buffer[index];
        buffer[index] = temporary;
    }
}
#endif
