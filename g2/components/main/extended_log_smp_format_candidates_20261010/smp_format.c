#include <stdint.h>

typedef struct { uint8_t *buffer; uint32_t capacity; uint32_t count; } writer;
static void put(writer *w, uint8_t c)
{
    if (w->capacity != 0u && w->count < w->capacity - 1u)
        w->buffer[w->count] = c;
    w->count++;
}
static void literal(writer *w, const char *p)
{
    while (*p != 0) put(w, (uint8_t)*p++);
}
static void string(writer *w, const uint8_t *p)
{
    if (p == (const uint8_t *)0) { literal(w, "(null)"); return; }
    while (*p != 0u) put(w, *p++);
}
static void decimal(writer *w, uint32_t raw)
{
    uint8_t reverse[10];
    uint32_t n = 0, negative = (raw & 0x80000000u) != 0u;
    uint32_t value = negative ? 0u - raw : raw;
    do { reverse[n++] = (uint8_t)('0' + value % 10u); value /= 10u; }
    while (value != 0u);
    if (negative) put(w, '-');
    while (n != 0u) put(w, reverse[--n]);
}

/* Bounded 0x44b76c contract for the two authenticated smpSmExecute format
 * literals. Precondition: format_word is 0x77bf14 or 0x765710. */
int32_t g2_log_candidate_smp_format(uint32_t destination_word,
                                    uint32_t capacity,
                                    uint32_t format_word,
                                    uint32_t arguments_word)
{
    writer w = {(uint8_t *)(uintptr_t)destination_word, capacity, 0u};
    const uint32_t *arguments = (const uint32_t *)(uintptr_t)arguments_word;
    if (format_word == 0x0077bf14u) {
        literal(&w, "SMP Exe: evt=");
        string(&w, (const uint8_t *)(uintptr_t)arguments[0]);
        literal(&w, " st=");
        string(&w, (const uint8_t *)(uintptr_t)arguments[1]);
    } else if (format_word == 0x00765710u) {
        literal(&w, "smpSmExecute event=");
        decimal(&w, arguments[0]);
        literal(&w, " state=");
        decimal(&w, arguments[1]);
    } else {
        __builtin_unreachable();
    }
    if (capacity != 0u)
        w.buffer[w.count < capacity ? w.count : capacity - 1u] = 0u;
    return (int32_t)w.count;
}
