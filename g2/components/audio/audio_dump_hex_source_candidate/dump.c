/* Stock Apollo 0x43dacc..0x43dc87, experimental source reconstruction.
 * Product RAM objects are explicit imports, not initialized guesses. */
#include <stdint.h>
#include <stdarg.h>

extern uint8_t g2_audio_dump_log_state[]; /* 0x20070be8, at least 0xf2 bytes */
extern char g2_audio_dump_buffer[1024]; /* 0x2006bd30 */
extern void g2_log_guard_enter(void);
extern void g2_log_guard_exit(void);
extern int32_t g2_log_contains(const char *, const char *);
extern uint32_t g2_log_append(uint32_t, char *, const char *);
extern void g2_log_transport_submit(uint32_t, uint32_t, uint32_t, uint32_t);
extern int32_t g2_log_vformat(char *, uint32_t, const char *, va_list);

#ifdef G2_DUMP_ORACLE
extern int32_t g2_audio_dump_snprintf(char *, uint32_t, const char *, ...);
#define dump_format g2_audio_dump_snprintf
#else
static int32_t dump_format(char *out, uint32_t capacity, const char *format, ...)
{
    va_list args;
    va_start(args, format);
    int32_t count = g2_log_vformat(out, capacity, format, args);
    va_end(args);
    return count;
}
#endif

void audio_dump_hex(const char *label, uint32_t width, const uint8_t *data,
                    uint32_t length)
{
    char temp[8] = {0};
    if (g2_audio_dump_log_state[0xf1] == 0 || g2_audio_dump_log_state[0] < 4)
        return;
    if (g2_log_contains(label, (const char *)g2_audio_dump_log_state + 1) == 0)
        return;
    g2_log_guard_enter();
    uint32_t base = 0;
    for (;;) {
        if ((uint16_t)base >= (uint16_t)length) break;
        const uint32_t last = ((uint8_t)width + (uint16_t)base - 1u);
        int32_t count = dump_format(g2_audio_dump_buffer, 1024,
                                    "D/HEX %s: %04X-%04X: ", label,
                                    (uint16_t)base, last);
        uint32_t used = (uint32_t)count < 1025u ? (uint32_t)count : 1024u;
        for (uint32_t column = 0; (uint16_t)column < (uint8_t)width; ++column) {
            if ((uint16_t)(base + (uint16_t)column) >= (uint16_t)length) {
                /* Stock memcpy helper copies up to 8 bytes, NUL included. */
                temp[0] = ' '; temp[1] = ' '; temp[2] = ' '; temp[3] = 0;
            } else {
                (void)dump_format(temp, sizeof temp, "%02X ",
                                  data[(uint16_t)(base + (uint16_t)column)]);
            }
            used += g2_log_append((uint16_t)used,g2_audio_dump_buffer+(uint16_t)used,temp);
            if (((uint16_t)(column+1u)&7u)==0u)
                used += g2_log_append((uint16_t)used,
                                      g2_audio_dump_buffer+(uint16_t)used," ");
        }
        used += g2_log_append((uint16_t)used,g2_audio_dump_buffer+(uint16_t)used,"  ");
        for (uint32_t column = 0; (uint16_t)column < (uint8_t)width; ++column) {
            const uint32_t index = (uint16_t)(base + (uint16_t)column);
            if (index >= (uint16_t)length) continue;
            uint8_t ch = data[index];
            if (ch < 32u || ch >= 127u) ch='.';
            (void)dump_format(temp,sizeof temp,"%c",ch);
            used += g2_log_append((uint16_t)used,
                                  g2_audio_dump_buffer+(uint16_t)used,temp);
        }
        if ((uint16_t)(used+1u)>=1025u) used=1023u;
        used += g2_log_append((uint16_t)used,g2_audio_dump_buffer+(uint16_t)used,"\n");
        g2_log_transport_submit((uint32_t)(uintptr_t)g2_audio_dump_buffer,
                                (uint16_t)used,0u,0u);
        base += (uint8_t)width;
    }
    g2_log_guard_exit();
}
