#include <stdint.h>

#define LOGGER_STATE ((volatile uint8_t *)(uintptr_t)0x20070be8u)
#define LOGGER_BUFFER ((uint8_t *)(uintptr_t)0x2006bd30u)

typedef struct {
    int32_t (*format)(uint32_t destination, uint32_t capacity,
                      uint32_t format, uint32_t arguments);
    uint32_t (*find_token)(uint32_t buffer, uint32_t token);
    void (*output)(uint32_t buffer, uint32_t length, uint32_t level);
    void (*guard_exit)(void);
} g2_log_postformat_providers;

uint32_t g2_log_candidate_append_normal(uint32_t, uint8_t *, const uint8_t *);

/* Local logger suffix 0x43d8dc..0x43d970, given the live format and
 * argument pointers. Lower variadic formatting and output remain callbacks. */
uint32_t g2_log_candidate_postformat(const g2_log_postformat_providers *p,
                                     uint32_t level, uint32_t offset,
                                     uint32_t format_word,
                                     uint32_t arguments_word)
{
    uint32_t remaining = 1024u - offset;
    int32_t written = p->format((uint32_t)(uintptr_t)(LOGGER_BUFFER + offset),
                                remaining, format_word, arguments_word);
    if (written >= 0 && (uint32_t)written + offset < 1025u)
        offset += (uint32_t)written;
    else offset = 1024u;
    if (offset + 5u >= 1025u) offset = 1019u;

    if (LOGGER_STATE[32] != 0u) {
        LOGGER_BUFFER[offset] = 0u;
        if (p->find_token((uint32_t)(uintptr_t)LOGGER_BUFFER,
                          (uint32_t)(uintptr_t)(LOGGER_STATE + 32u)) == 0u) {
            p->guard_exit();
            return offset;
        }
    }
    if (LOGGER_STATE[245] != 0u)
        offset += g2_log_candidate_append_normal(
            offset, LOGGER_BUFFER + offset,
            (const uint8_t *)(uintptr_t)0x0078d4fcu);
    offset += g2_log_candidate_append_normal(
        offset, LOGGER_BUFFER + offset,
        (const uint8_t *)(uintptr_t)0x0043da80u);
    p->output((uint32_t)(uintptr_t)LOGGER_BUFFER, offset, (uint8_t)level);
    p->guard_exit();
    return offset;
}
