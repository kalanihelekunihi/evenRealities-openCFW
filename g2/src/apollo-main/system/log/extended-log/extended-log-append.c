#include <stdint.h>

/* Non-null input branch of 0x44b668. The caller supplies the current
 * buffer offset, destination cursor, and NUL-terminated source. No terminator
 * is written by this primitive; it returns the bytes copied. */
uint32_t g2_log_candidate_append_normal(uint32_t offset,
                                        uint8_t *destination,
                                        const uint8_t *source)
{
    const uint8_t *begin = source;
    while (*source != 0u && offset < 1024u) {
        *destination++ = *source++;
        offset++;
    }
    return (uint32_t)(source - begin);
}
